import hashlib
import json
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.tools.base import BaseTool
from app.models.models import Worker
from app.utils.embeddings import embed_text
from app.database.redis import redis_client

SEARCH_CACHE_TTL = 300  # 5 minutes


# Metro area clusters — searching for a city also surfaces workers from nearby cities.
# This means a business in SF won't miss a great worker who listed Oakland.
METRO_CLUSTERS: dict[str, list[str]] = {
    "san francisco": ["san francisco", "oakland", "berkeley", "san jose", "fremont", "palo alto"],
    "los angeles":   ["los angeles", "santa monica", "long beach", "pasadena", "burbank"],
    "san diego":     ["san diego", "chula vista", "los angeles"],
    "new york":      ["new york", "brooklyn", "queens", "bronx", "jersey city", "hoboken"],
    "chicago":       ["chicago", "evanston", "oak park"],
    "boston":        ["boston", "cambridge", "somerville"],
    "miami":         ["miami", "fort lauderdale", "hialeah"],
    "seattle":       ["seattle", "bellevue", "tacoma", "redmond"],
    "portland":      ["portland", "beaverton", "gresham"],
    "denver":        ["denver", "aurora", "boulder", "lakewood"],
    "austin":        ["austin", "round rock", "cedar park"],
    "nashville":     ["nashville", "murfreesboro"],
    "atlanta":       ["atlanta", "decatur", "sandy springs"],
    "las vegas":     ["las vegas", "henderson", "north las vegas"],
    "phoenix":       ["phoenix", "scottsdale", "tempe", "mesa"],
}


def _metro_cities(location: str) -> list[str]:
    """Return all cities in the same metro area as the given location string."""
    loc_lower = location.lower()
    for anchor, cluster in METRO_CLUSTERS.items():
        if anchor in loc_lower:
            return cluster
    # no known cluster — fall back to the raw location
    return [loc_lower]


def _blend_vectors(business_vec: list[float], query_vec: list[float], business_weight: float = 0.4) -> list[float]:
    """
    Weighted average of business embedding and query embedding, then L2-normalised.

    business_weight=0.4 means: 40% business culture fit, 60% query relevance.
    Normalising is required because pgvector's <=> uses cosine distance,
    which compares direction — not magnitude. A un-normalised blend would
    give the wrong distances.
    """
    q_weight = 1.0 - business_weight
    blended = [business_weight * b + q_weight * q for b, q in zip(business_vec, query_vec)]

    magnitude = math.sqrt(sum(x * x for x in blended))
    if magnitude == 0:
        return blended
    return [x / magnitude for x in blended]


class SearchWorkersTool(BaseTool):
    name = "search_workers"
    description = "Search for workers that match a business's requirements using semantic similarity and field filters."

    def __init__(self, db: AsyncSession, business=None):
        self.db = db
        self.business = business  # used to blend business culture into the search vector

    async def execute(
        self,
        query: str,
        profession: str | None = None,
        location: str | None = None,
        availability: str | None = None,
        experience_years: int | None = None,
        shift_date: str | None = None,
        day_of_week: str | None = None,
        limit: int = 10,
    ) -> dict:
        business_id = self.business.id if self.business else 0
        cache_params = {
            "query": query, "profession": profession, "location": location,
            "availability": availability, "experience_years": experience_years,
            "shift_date": shift_date, "day_of_week": day_of_week, "limit": limit,
        }
        cache_key = f"qs:sw:{business_id}:{hashlib.sha256(json.dumps(cache_params, sort_keys=True).encode()).hexdigest()}"
        redis = redis_client.get()
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # build enriched query for embedding — profession, experience, and date
        # all go in here as soft signals, not hard SQL filters
        enriched_query = query
        if profession:
            enriched_query = f"{profession} — {enriched_query}"
        if experience_years:
            enriched_query += f" with at least {experience_years} years of experience"
        if shift_date:
            enriched_query += f" on {shift_date}"
        if day_of_week:
            enriched_query += f" ({day_of_week})"

        query_vector = await embed_text(enriched_query)

        # A — blend business culture embedding into the search vector
        # workers who fit the business environment rank higher even without explicit keywords
        if self.business is not None and self.business.embedding is not None:
            search_vector = _blend_vectors(self.business.embedding, query_vector)
        else:
            search_vector = query_vector

        # Stage 1: SQL hard filters — profession, location (metro-expanded), availability
        # these are all binary constraints, apply them first to narrow the pool
        stmt = select(Worker).where(Worker.embedding.isnot(None))

        if profession:
            stmt = stmt.where(Worker.profession.ilike(f"%{profession}%"))

        if location:
            metro = _metro_cities(location)
            location_filter = Worker.location.ilike(f"%{metro[0]}%")
            for city in metro[1:]:
                location_filter = location_filter.__or__(Worker.location.ilike(f"%{city}%"))
            stmt = stmt.where(location_filter)

        if availability:
            stmt = stmt.where(Worker.availability.ilike(f"%{availability}%"))

        # Stage 2: rank the filtered pool by vector similarity (cultural + query fit)
        stmt = stmt.order_by(Worker.embedding.op("<=>")(search_vector)).limit(limit)

        result = await self.db.execute(stmt)
        workers = result.scalars().all()

        payload = {
            "workers": [
                {
                    "id": w.id,
                    "name": w.name,
                    "profession": w.profession,
                    "location": w.location,
                    "skills": w.skills,
                    "experience_years": w.experience_years,
                    "availability": w.availability,
                    "bio": w.bio,
                }
                for w in workers
            ]
        }
        await redis.setex(cache_key, SEARCH_CACHE_TTL, json.dumps(payload))
        return payload

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language description of the ideal worker — include role, environment, personality fit, and business vibe",
                        },
                        "profession": {
                            "type": "string",
                            "description": "Role being searched for e.g. bartender, barista, line cook. Added to the semantic query, not an exact SQL filter.",
                        },
                        "location": {
                            "type": "string",
                            "description": "City the worker should be in. Nearby metro cities are automatically included.",
                        },
                        "availability": {
                            "type": "string",
                            "description": "When the worker needs to be available e.g. Weekdays, Weekends, Evenings, Mornings, Nights",
                        },
                        "experience_years": {
                            "type": "integer",
                            "description": "Minimum years of experience preferred. Soft signal — influences ranking, not a hard cutoff.",
                        },
                        "shift_date": {
                            "type": "string",
                            "description": "Specific date of the shift in YYYY-MM-DD format",
                        },
                        "day_of_week": {
                            "type": "string",
                            "description": "Day of the week e.g. Monday, Saturday",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of workers to return",
                        },
                    },
                    "required": ["query"],
                },
            },
        }

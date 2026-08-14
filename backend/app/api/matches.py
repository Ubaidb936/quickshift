from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.database.db import get_db
from app.models.models import Match, Shift
from app.utils.schemas import MatchResponse
from app.auth import require_business, require_worker
from app.logger import get_logger

router = APIRouter(prefix="/matches", tags=["matches"])
logger = get_logger("matches")

# Reusable load options — always need worker + shift when building a MatchResponse
_MATCH_OPTIONS = [selectinload(Match.worker), selectinload(Match.shift)]


def _to_response(m: Match) -> MatchResponse:
    return MatchResponse(
        id=m.id,
        shift_id=m.shift_id,
        worker_id=m.worker_id,
        business_id=m.business_id,
        status=m.status,
        worker_name=m.worker.name,
        worker_profession=m.worker.profession,
        worker_location=m.worker.location,
        shift_position=m.shift.position,
        shift_pay_rate=m.shift.pay_rate,
    )


# NOTE: /my-matches and /interested/{shift_id} must be before /{match_id}/...
@router.get("/my-matches", response_model=List[MatchResponse])
async def get_my_matches(db: AsyncSession = Depends(get_db), user=Depends(require_worker)):
    result = await db.execute(
        select(Match).where(Match.worker_id == user["id"]).options(*_MATCH_OPTIONS)
    )
    return [_to_response(m) for m in result.scalars().all()]


@router.get("/interested/{shift_id}", response_model=List[MatchResponse])
async def get_interested(shift_id: int, db: AsyncSession = Depends(get_db), user=Depends(require_business)):
    shift_result = await db.execute(
        select(Shift).where(Shift.id == shift_id, Shift.business_id == user["id"])
    )
    if not shift_result.scalars().first():
        raise HTTPException(status_code=404, detail="Shift not found")

    result = await db.execute(
        select(Match).where(Match.shift_id == shift_id).options(*_MATCH_OPTIONS)
    )
    return [_to_response(m) for m in result.scalars().all()]


@router.post("/interest/{shift_id}", response_model=MatchResponse)
async def show_interest(shift_id: int, db: AsyncSession = Depends(get_db), user=Depends(require_worker)):
    shift_result = await db.execute(
        select(Shift).where(Shift.id == shift_id, Shift.status == "active")
    )
    shift = shift_result.scalars().first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found or not active")

    existing_result = await db.execute(
        select(Match).where(Match.shift_id == shift_id, Match.worker_id == user["id"])
    )
    if existing_result.scalars().first():
        logger.warning("Duplicate interest attempt", extra={"worker_id": user["id"], "shift_id": shift_id})
        raise HTTPException(status_code=400, detail="Already shown interest in this shift")

    match = Match(
        business_id=shift.business_id,
        worker_id=user["id"],
        shift_id=shift_id,
        status="interested",
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)

    # reload with relationships so _to_response can access match.worker and match.shift
    result = await db.execute(
        select(Match).where(Match.id == match.id).options(*_MATCH_OPTIONS)
    )
    match = result.scalars().first()

    logger.info("Worker showed interest", extra={"match_id": match.id, "worker_id": user["id"], "shift_id": shift_id})
    return _to_response(match)


@router.patch("/{match_id}/accept")
async def accept_worker(match_id: int, db: AsyncSession = Depends(get_db), user=Depends(require_business)):
    result = await db.execute(
        select(Match).where(Match.id == match_id, Match.business_id == user["id"])
    )
    match = result.scalars().first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "accepted"
    await db.commit()
    logger.info("Worker accepted", extra={"match_id": match_id, "worker_id": match.worker_id, "business_id": user["id"]})
    return {"status": "accepted"}


@router.patch("/{match_id}/decline")
async def decline_worker(match_id: int, db: AsyncSession = Depends(get_db), user=Depends(require_business)):
    result = await db.execute(
        select(Match).where(Match.id == match_id, Match.business_id == user["id"])
    )
    match = result.scalars().first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "declined"
    await db.commit()
    logger.info("Worker declined", extra={"match_id": match_id, "worker_id": match.worker_id, "business_id": user["id"]})
    return {"status": "declined"}


@router.patch("/{match_id}/unavailable")
async def mark_unavailable(match_id: int, db: AsyncSession = Depends(get_db), user=Depends(require_worker)):
    result = await db.execute(
        select(Match).where(Match.id == match_id, Match.worker_id == user["id"])
    )
    match = result.scalars().first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "unavailable"
    await db.commit()
    logger.info("Worker marked unavailable", extra={"match_id": match_id, "worker_id": user["id"]})
    return {"status": "unavailable"}

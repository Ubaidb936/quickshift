from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.models.models import Business, Worker
from app.utils.schemas import BusinessRegister, WorkerRegister, LoginRequest, TokenResponse
from app.auth import hash_password, verify_password, create_token, get_current_user, security
from app.database.redis import redis_client
from app.utils.embeddings import build_business_text, build_worker_text, embed_text
from app.utils.cache import invalidate_search_cache
from app.logger import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger("auth")


@router.post("/register/business", response_model=TokenResponse)
async def register_business(data: BusinessRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Business).where(Business.email == data.email))
    if result.scalars().first():
        logger.warning("Business registration failed — email already exists", extra={"email": data.email})
        raise HTTPException(status_code=400, detail="Email already registered")

    business = Business(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        location=data.location,
        working_hours=data.working_hours,
        phone=data.phone,
        logo_url=data.logo_url,
        industry=data.industry,
        description=data.description,
        vibe=data.vibe,
        team_size=data.team_size,
    )
    db.add(business)
    await db.commit()
    await db.refresh(business)

    text = build_business_text(business)
    business.embedding = await embed_text(text)
    await db.commit()

    logger.info("Business registered", extra={"business_id": business.id, "business_name": business.name})
    token = create_token({"sub": business.email, "role": "business", "id": business.id})
    return TokenResponse(access_token=token, role="business", user_id=business.id, name=business.name)


@router.post("/register/worker", response_model=TokenResponse)
async def register_worker(data: WorkerRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Worker).where(Worker.email == data.email))
    if result.scalars().first():
        logger.warning("Worker registration failed — email already exists", extra={"email": data.email})
        raise HTTPException(status_code=400, detail="Email already registered")

    worker = Worker(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        location=data.location,
        profession=data.profession,
        skills=data.skills,
        experience_years=data.experience_years,
        availability=data.availability,
        bio=data.bio,
    )
    db.add(worker)
    await db.commit()
    await db.refresh(worker)

    text = build_worker_text(worker)
    worker.embedding = await embed_text(text)
    await db.commit()

    redis = redis_client.get()
    deleted = await invalidate_search_cache(redis)
    logger.info(
        "Search cache invalidated after worker registration",
        extra={"worker_id": worker.id, "keys_deleted": deleted},
    )

    logger.info("Worker registered", extra={"worker_id": worker.id, "worker_name": worker.name, "profession": worker.profession})
    token = create_token({"sub": worker.email, "role": "worker", "id": worker.id})
    return TokenResponse(access_token=token, role="worker", user_id=worker.id, name=worker.name)


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    redis = redis_client.get()
    rate_key = f"rate:login:{request.client.host}"
    attempts = await redis.get(rate_key)
    if attempts and int(attempts) >= 5:
        logger.warning("Login blocked — rate limit exceeded", extra={"ip": request.client.host})
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again in 60 seconds.")

    if data.role == "business":
        result = await db.execute(select(Business).where(Business.email == data.email))
        user = result.scalars().first()
    elif data.role == "worker":
        result = await db.execute(select(Worker).where(Worker.email == data.email))
        user = result.scalars().first()
    else:
        raise HTTPException(status_code=400, detail="Role must be 'business' or 'worker'")

    if not user or not verify_password(data.password, user.password):
        await redis.incr(rate_key)
        await redis.expire(rate_key, 60)
        logger.warning("Login failed — invalid credentials", extra={"email": data.email, "role": data.role})
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await redis.delete(rate_key)
    logger.info("Login successful", extra={"user_id": user.id, "role": data.role})
    token = create_token({"sub": user.email, "role": data.role, "id": user.id})
    return TokenResponse(access_token=token, role=data.role, user_id=user.id, name=user.name)


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), user=Depends(get_current_user)):
    token = credentials.credentials
    ttl = int(user.get("exp") - datetime.now(timezone.utc).timestamp())
    if ttl > 0:
        await redis_client.get().setex(f"blacklist:{token}", ttl, "1")
    logger.info("User logged out", extra={"user_id": user["id"], "role": user["role"]})
    return {"detail": "Logged out"}

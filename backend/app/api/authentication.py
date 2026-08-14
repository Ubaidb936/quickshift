from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.models.models import Business, Worker
from app.utils.schemas import BusinessRegister, WorkerRegister, LoginRequest, TokenResponse
from app.auth import hash_password, verify_password, create_token
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
    )
    db.add(business)
    await db.commit()
    await db.refresh(business)

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
    )
    db.add(worker)
    await db.commit()
    await db.refresh(worker)

    logger.info("Worker registered", extra={"worker_id": worker.id, "worker_name": worker.name, "profession": worker.profession})
    token = create_token({"sub": worker.email, "role": "worker", "id": worker.id})
    return TokenResponse(access_token=token, role="worker", user_id=worker.id, name=worker.name)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    if data.role == "business":
        result = await db.execute(select(Business).where(Business.email == data.email))
        user = result.scalars().first()
    elif data.role == "worker":
        result = await db.execute(select(Worker).where(Worker.email == data.email))
        user = result.scalars().first()
    else:
        raise HTTPException(status_code=400, detail="Role must be 'business' or 'worker'")

    if not user or not verify_password(data.password, user.password):
        logger.warning("Login failed — invalid credentials", extra={"email": data.email, "role": data.role})
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info("Login successful", extra={"user_id": user.id, "role": data.role})
    token = create_token({"sub": user.email, "role": data.role, "id": user.id})
    return TokenResponse(access_token=token, role=data.role, user_id=user.id, name=user.name)

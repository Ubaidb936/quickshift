from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.database.db import get_db
from app.models.models import Shift
from app.utils.schemas import ShiftCreate, ShiftUpdate, ShiftResponse
from app.auth import require_business, get_current_user
from app.logger import get_logger

router = APIRouter(prefix="/shifts", tags=["shifts"])
logger = get_logger("shifts")


def _to_response(shift: Shift) -> ShiftResponse:
    return ShiftResponse(
        **{c.name: getattr(shift, c.name) for c in shift.__table__.columns},
        business_name=shift.business.name,
        business_location=shift.business.location,
    )


@router.post("/", response_model=ShiftResponse)
async def post_shift(data: ShiftCreate, db: AsyncSession = Depends(get_db), user=Depends(require_business)):
    shift = Shift(
        business_id=user["id"],
        position=data.position,
        start_time=data.start_time,
        end_time=data.end_time,
        pay_rate=data.pay_rate,
        duties=data.duties,
        attire=data.attire,
        num_workers=data.num_workers,
    )
    db.add(shift)
    await db.commit()
    await db.refresh(shift)

    # reload with business eagerly so _to_response can access shift.business
    result = await db.execute(
        select(Shift).where(Shift.id == shift.id).options(selectinload(Shift.business))
    )
    shift = result.scalars().first()

    logger.info("Shift posted", extra={"shift_id": shift.id, "business_id": user["id"], "position": shift.position})
    return _to_response(shift)


# NOTE: /my-shifts must be defined before /{shift_id} to avoid route conflict
@router.get("/my-shifts", response_model=List[ShiftResponse])
async def get_my_shifts(db: AsyncSession = Depends(get_db), user=Depends(require_business)):
    result = await db.execute(
        select(Shift)
        .where(Shift.business_id == user["id"])
        .options(selectinload(Shift.business))
    )
    shifts = result.scalars().all()
    return [_to_response(s) for s in shifts]


@router.get("/", response_model=List[ShiftResponse])
async def get_shifts(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(Shift)
        .where(Shift.status == "active")
        .options(selectinload(Shift.business))
    )
    shifts = result.scalars().all()
    return [_to_response(s) for s in shifts]


@router.get("/{shift_id}", response_model=ShiftResponse)
async def get_shift(shift_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(Shift).where(Shift.id == shift_id).options(selectinload(Shift.business))
    )
    shift = result.scalars().first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return _to_response(shift)


@router.patch("/{shift_id}", response_model=ShiftResponse)
async def edit_shift(shift_id: int, data: ShiftUpdate, db: AsyncSession = Depends(get_db), user=Depends(require_business)):
    result = await db.execute(
        select(Shift)
        .where(Shift.id == shift_id, Shift.business_id == user["id"])
        .options(selectinload(Shift.business))
    )
    shift = result.scalars().first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(shift, field, value)
    await db.commit()
    await db.refresh(shift)
    logger.info("Shift updated", extra={"shift_id": shift_id, "business_id": user["id"]})
    return _to_response(shift)


@router.patch("/{shift_id}/pause")
async def pause_shift(shift_id: int, db: AsyncSession = Depends(get_db), user=Depends(require_business)):
    result = await db.execute(
        select(Shift).where(Shift.id == shift_id, Shift.business_id == user["id"])
    )
    shift = result.scalars().first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    shift.status = "paused" if shift.status == "active" else "active"
    await db.commit()
    logger.info("Shift status toggled", extra={"shift_id": shift_id, "new_status": shift.status, "business_id": user["id"]})
    return {"status": shift.status}


@router.delete("/{shift_id}")
async def delete_shift(shift_id: int, db: AsyncSession = Depends(get_db), user=Depends(require_business)):
    result = await db.execute(
        select(Shift).where(Shift.id == shift_id, Shift.business_id == user["id"])
    )
    shift = result.scalars().first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    shift.status = "deleted"
    await db.commit()
    logger.info("Shift deleted", extra={"shift_id": shift_id, "business_id": user["id"]})
    return {"detail": "Shift deleted"}

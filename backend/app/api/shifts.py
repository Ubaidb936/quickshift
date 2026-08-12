from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.models.models import Shift
from app.utils.schemas import ShiftCreate, ShiftUpdate, ShiftResponse
from app.auth import require_business, get_current_user

router = APIRouter(prefix="/shifts", tags=["shifts"])


def _to_response(shift: Shift) -> ShiftResponse:
    return ShiftResponse(
        **{c.name: getattr(shift, c.name) for c in shift.__table__.columns},
        business_name=shift.business.name,
        business_location=shift.business.location,
    )


@router.post("/", response_model=ShiftResponse)
def post_shift(data: ShiftCreate, db: Session = Depends(get_db), user=Depends(require_business)):
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
    db.commit()
    db.refresh(shift)
    return _to_response(shift)


# NOTE: /my-shifts must be defined before /{shift_id} to avoid route conflict
@router.get("/my-shifts", response_model=List[ShiftResponse])
def get_my_shifts(db: Session = Depends(get_db), user=Depends(require_business)):
    shifts = db.query(Shift).filter(Shift.business_id == user["id"]).all()
    return [_to_response(s) for s in shifts]


@router.get("/", response_model=List[ShiftResponse])
def get_shifts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    shifts = db.query(Shift).filter(Shift.status == "active").all()
    return [_to_response(s) for s in shifts]


@router.get("/{shift_id}", response_model=ShiftResponse)
def get_shift(shift_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return _to_response(shift)


@router.patch("/{shift_id}", response_model=ShiftResponse)
def edit_shift(shift_id: int, data: ShiftUpdate, db: Session = Depends(get_db), user=Depends(require_business)):
    shift = db.query(Shift).filter(Shift.id == shift_id, Shift.business_id == user["id"]).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(shift, field, value)
    db.commit()
    db.refresh(shift)
    return _to_response(shift)


@router.patch("/{shift_id}/pause")
def pause_shift(shift_id: int, db: Session = Depends(get_db), user=Depends(require_business)):
    shift = db.query(Shift).filter(Shift.id == shift_id, Shift.business_id == user["id"]).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    shift.status = "paused" if shift.status == "active" else "active"
    db.commit()
    return {"status": shift.status}


@router.delete("/{shift_id}")
def delete_shift(shift_id: int, db: Session = Depends(get_db), user=Depends(require_business)):
    shift = db.query(Shift).filter(Shift.id == shift_id, Shift.business_id == user["id"]).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    shift.status = "deleted"
    db.commit()
    return {"detail": "Shift deleted"}

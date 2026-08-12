from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.models.models import Match, Shift
from app.utils.schemas import MatchResponse
from app.auth import require_business, require_worker

router = APIRouter(prefix="/matches", tags=["matches"])


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
def get_my_matches(db: Session = Depends(get_db), user=Depends(require_worker)):
    matches = db.query(Match).filter(Match.worker_id == user["id"]).all()
    return [_to_response(m) for m in matches]


@router.get("/interested/{shift_id}", response_model=List[MatchResponse])
def get_interested(shift_id: int, db: Session = Depends(get_db), user=Depends(require_business)):
    shift = db.query(Shift).filter(Shift.id == shift_id, Shift.business_id == user["id"]).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    matches = db.query(Match).filter(Match.shift_id == shift_id).all()
    return [_to_response(m) for m in matches]


@router.post("/interest/{shift_id}", response_model=MatchResponse)
def show_interest(shift_id: int, db: Session = Depends(get_db), user=Depends(require_worker)):
    shift = db.query(Shift).filter(Shift.id == shift_id, Shift.status == "active").first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found or not active")
    existing = db.query(Match).filter(Match.shift_id == shift_id, Match.worker_id == user["id"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already shown interest in this shift")
    match = Match(
        business_id=shift.business_id,
        worker_id=user["id"],
        shift_id=shift_id,
        status="interested",
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return _to_response(match)


@router.patch("/{match_id}/accept")
def accept_worker(match_id: int, db: Session = Depends(get_db), user=Depends(require_business)):
    match = db.query(Match).filter(Match.id == match_id, Match.business_id == user["id"]).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "accepted"
    db.commit()
    return {"status": "accepted"}


@router.patch("/{match_id}/decline")
def decline_worker(match_id: int, db: Session = Depends(get_db), user=Depends(require_business)):
    match = db.query(Match).filter(Match.id == match_id, Match.business_id == user["id"]).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "declined"
    db.commit()
    return {"status": "declined"}


@router.patch("/{match_id}/unavailable")
def mark_unavailable(match_id: int, db: Session = Depends(get_db), user=Depends(require_worker)):
    match = db.query(Match).filter(Match.id == match_id, Match.worker_id == user["id"]).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "unavailable"
    db.commit()
    return {"status": "unavailable"}

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# --- Auth ---

class BusinessRegister(BaseModel):
    name: str
    email: str
    password: str
    location: Optional[str] = None
    working_hours: Optional[str] = None


class WorkerRegister(BaseModel):
    name: str
    email: str
    password: str
    location: Optional[str] = None
    profession: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str
    role: str  # "business" or "worker"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str


# --- Shifts ---

class ShiftCreate(BaseModel):
    position: str
    start_time: datetime
    end_time: datetime
    pay_rate: float
    duties: Optional[str] = None
    attire: Optional[str] = None
    num_workers: int = 1


class ShiftUpdate(BaseModel):
    position: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pay_rate: Optional[float] = None
    duties: Optional[str] = None
    attire: Optional[str] = None
    num_workers: Optional[int] = None


class ShiftResponse(BaseModel):
    id: int
    business_id: int
    position: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    pay_rate: Optional[float]
    duties: Optional[str]
    attire: Optional[str]
    num_workers: int
    status: str
    business_name: Optional[str] = None
    business_location: Optional[str] = None

    class Config:
        from_attributes = True


# --- Matches ---

class MatchResponse(BaseModel):
    id: int
    shift_id: int
    worker_id: int
    business_id: int
    status: str
    worker_name: Optional[str] = None
    worker_profession: Optional[str] = None
    worker_location: Optional[str] = None
    shift_position: Optional[str] = None
    shift_pay_rate: Optional[float] = None

    class Config:
        from_attributes = True

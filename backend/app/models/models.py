from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.db import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    location = Column(String)
    working_hours = Column(String)

    shifts = relationship("Shift", back_populates="business")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    location = Column(String)
    profession = Column(String)

    matches = relationship("Match", back_populates="worker")


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    position = Column(String, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    pay_rate = Column(Float)
    duties = Column(Text)
    attire = Column(String)
    num_workers = Column(Integer, default=1)
    status = Column(String, default="active")  # active / paused / deleted

    business = relationship("Business", back_populates="shifts")
    matches = relationship("Match", back_populates="shift")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    status = Column(String, default="interested")  # interested / accepted / declined / unavailable

    business = relationship("Business")
    worker = relationship("Worker", back_populates="matches")
    shift = relationship("Shift", back_populates="matches")

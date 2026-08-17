from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database.db import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    location = Column(String)
    working_hours = Column(String)
    phone = Column(String)
    logo_url = Column(String)
    industry = Column(String)
    description = Column(Text)
    vibe = Column(String)       # comma-separated tags: "fast-paced,upscale,indoor"
    team_size = Column(String)  # small / medium / large
    embedding = Column(Vector(1536), nullable=True)  # OpenAI text-embedding-3-small

    shifts = relationship("Shift", back_populates="business")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    location = Column(String)
    profession = Column(String)
    skills = Column(String)
    experience_years = Column(Integer)
    availability = Column(String)
    bio = Column(Text)
    embedding = Column(Vector(1536), nullable=True)

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


class AgentConversation(Base):
    __tablename__ = "agent_conversations"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    tool_called = Column(String, nullable=True)
    tool_args = Column(JSON, nullable=True)
    result_count = Column(Integer, nullable=True)
    agent_response = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    latency_ms = Column(Float, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="success")

    business = relationship("Business")


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

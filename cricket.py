# cricket.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.mysql import JSON
from database import get_db, Base
from datetime import datetime
from typing import List

router = APIRouter()

# Cricket Match Event Database Model
class CricketMatchEvent(Base):
    __tablename__ = "cricket_match"
    id = Column(Integer, primary_key=True, index=True)
    match_name = Column(String(100), nullable=False)
    team_1 = Column(String(255), nullable=False)
    team_2 = Column(String(255), nullable=False)
    match_date = Column(DateTime, nullable=False)
    venue = Column(String(255), nullable=False)
    team_1_players = Column(JSON, nullable=False)
    team_2_players = Column(JSON, nullable=False)

class CricketMatchEventCreate(BaseModel):
    match_name: str
    team_1: str
    team_2: str
    match_date: datetime
    venue: str
    team_1_players: List[str]
    team_2_players: List[str]

class CricketMatchEventOut(CricketMatchEventCreate):
    id: int

    class Config:
        orm_mode = True

@router.post("/cricket_event/", response_model=CricketMatchEventOut)
def create_cricket_event(event: CricketMatchEventCreate, db: Session = Depends(get_db)):
    db_event = CricketMatchEvent(
        match_name=event.match_name,
        team_1=event.team_1,
        team_2=event.team_2,
        match_date=event.match_date,
        venue=event.venue,
        team_1_players=event.team_1_players,
        team_2_players=event.team_2_players,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/matches/", response_model=List[CricketMatchEventOut])
def get_matches(db: Session = Depends(get_db)):
    return db.query(CricketMatchEvent).all()

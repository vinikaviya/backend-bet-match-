from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.mysql import JSON  # For MySQL JSON datatype
from .database import Base

# Table Definition for User
class User(Base):
    __tablename__ = "user_register"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    date_of_birth = Column(String(20))
    email = Column(String(100), unique=True)  # Ensure unique email
    hashed_password = Column(String(255))  # Store hashed password
    phone = Column(String(15))

# Table Definition for Admin
class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))

# Table Definition for Cricket Match Event
class CricketMatchEvent(Base):
    __tablename__ = "cricket_match"
    id = Column(Integer, primary_key=True, index=True)
    match_name = Column(String(100), nullable=False)
    team_1 = Column(String(255), nullable=False)
    team_2 = Column(String(255), nullable=False)
    match_date = Column(DateTime, nullable=False)
    venue = Column(String(255), nullable=False)
    
    # JSON columns for storing players for each team
    team_1_players = Column(JSON, nullable=False)  # List of players for team 1
    team_2_players = Column(JSON, nullable=False)  # List of players for team 2

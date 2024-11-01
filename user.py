from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db, Base
from sqlalchemy import Column, Integer, String
from cricket import CricketMatchEvent

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User Database Model
class User(Base):
    __tablename__ = "user_register"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    date_of_birth = Column(String(20))
    email = Column(String(100), unique=True)  
    hashed_password = Column(String(255))  
    phone = Column(String(15))

class UserRequest(BaseModel):
    full_name: str
    date_of_birth: str
    email: str
    password: str
    phone: str

class UserLogin(BaseModel):
    email: str
    password: str

class MatchID(BaseModel):
    id: int

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/user_register/")
def create_user(user: UserRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    db_user = User(
        full_name=user.full_name,
        date_of_birth=user.date_of_birth,
        email=user.email,
        hashed_password=hashed_password,
        phone=user.phone,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully", "user_id": db_user.id}

@router.post("/user_login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    matches = db.query(CricketMatchEvent).all()
    formatted_matches = [f"{match.team_1} vs {match.team_2}" for match in matches]
    return {"matches": formatted_matches}

@router.get("/matches/{match_id}")
def get_match(match_id: int, db: Session = Depends(get_db)):
    # Query the database for a specific match by ID
    match = db.query(CricketMatchEvent).filter(CricketMatchEvent.id == match_id).first()

    # Check if the match exists
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    return {
        "match": match 
    }

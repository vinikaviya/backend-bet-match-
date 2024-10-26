# admin.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, Base
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String
from cricket import CricketMatchEvent

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Admin Database Model
class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))

class AdminRequest(BaseModel):
    email: str
    password: str

class AdminLogin(BaseModel):
    email: str
    password: str

@router.post("/admin_register/")
def create_admin(admin: AdminRequest, db: Session = Depends(get_db)):
    existing_admin = db.query(Admin).filter(Admin.email == admin.email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin email already registered")
    
    hashed_password = pwd_context.hash(admin.password)
    db_admin = Admin(email=admin.email, hashed_password=hashed_password)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return {"message": "Admin created successfully", "admin_id": db_admin.id}

@router.post("/admin_login/")
def admin_login(admin: AdminLogin, db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(Admin.email == admin.email).first()
    if not db_admin or not pwd_context.verify(admin.password, db_admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    matches = db.query(CricketMatchEvent).all()
    return {"matches": matches}

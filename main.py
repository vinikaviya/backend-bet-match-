from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import OperationalError
from sqlalchemy.dialects.mysql import JSON  # For MySQL JSON datatype
from passlib.context import CryptContext
from datetime import datetime
from typing import List


DATABASE_URL = "mysql+pymysql://root:vinikaviya2003@localhost:3306/betting"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Function to create the database if it doesn't exist
def create_database_if_not_exists():
    db_engine = create_engine("mysql+pymysql://root:vinikaviya2003@localhost:3306/")
    with db_engine.connect() as connection:
        try:
            connection.execute(text("CREATE DATABASE IF NOT EXISTS betting"))
        except OperationalError as e:
            print(f"Error creating database: {e}")

create_database_if_not_exists()


class User(Base):
    __tablename__ = "user_register"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    date_of_birth = Column(String(20))
    email = Column(String(100), unique=True)  
    hashed_password = Column(String(255))  
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
    
 
    team_1_players = Column(JSON, nullable=False)  
    team_2_players = Column(JSON, nullable=False)  

# ------------------------Pydantic models -------------------------------


class UserRequest(BaseModel):
    full_name: str
    date_of_birth: str
    email: str
    password: str
    phone: str

class UserLogin(BaseModel):
    email: str
    password: str

class AdminRequest(BaseModel):
    email: str
    password: str

class AdminLogin(BaseModel):
    email: str
    password: str

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
        from_attributes = True  # Pydantic V2 replacement for orm_mode


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@app.on_event("startup")
def on_startup():
    try:
        with engine.connect() as connection:
            print("Database connection successful.")
            Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        print(f"Database connection failed: {e}")

# -----------------------Endpoint to add user data---------------------------------

@app.post("/user_register/")
def create_user(user: UserRequest, db: Session = Depends(get_db)):
    # Check if the email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before storing
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
    return {
        "message": "User created successfully",
        "user": {
            "id": db_user.id,
            "full_name": db_user.full_name,
            "date_of_birth": db_user.date_of_birth,
            "email": db_user.email,
            "phone": db_user.phone,
        },
    }

#-------------------- User Login and Fetch Cricket Events----------------------------

@app.post("/user_login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    matches = db.query(CricketMatchEvent).all()
    formatted_matches=[f"{match.team_1}vs{match.team_2}"for match in matches]

    return {
        "matches": formatted_matches  
    }

# --------------------------Endpoint to add admin data-------------------------

@app.post("/admin_register/")
def create_admin(admin: AdminRequest, db: Session = Depends(get_db)):
    # Check if the admin email already exists
    existing_admin = db.query(Admin).filter(Admin.email == admin.email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin email already registered")
    
    # Hash the password before storing
    hashed_password = hash_password(admin.password)
    
    db_admin = Admin(
        email=admin.email,
        hashed_password=hashed_password,
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return {"message": "Admin created successfully", "admin_id": db_admin.id}

# ----------------------Admin Login and Fetch Cricket Events------------------

@app.post("/admin_login/")
def admin_login(admin: AdminLogin, db: Session = Depends(get_db)):
    # Query the database for the admin
    db_admin = db.query(Admin).filter(Admin.email == admin.email).first()

    # Check if admin exists and password matches
    if not db_admin or not verify_password(admin.password, db_admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    # Fetch all cricket matches after successful login
    matches = db.query(CricketMatchEvent).all()

    return {
        "matches": matches  # Returning the cricket events
    }

# ---------------------POST endpoint to create a cricket match event-----------------------

@app.post("/cricket_event/", response_model=CricketMatchEventOut)
def create_cricket_event(event: CricketMatchEventCreate, db: Session = Depends(get_db)):
    try:
        # Create a new cricket match event in the database
        db_event = CricketMatchEvent(
            match_name=event.match_name,
            team_1=event.team_1,
            team_2=event.team_2,
            match_date=event.match_date,
            venue=event.venue,
            team_1_players=event.team_1_players,  # List of players for team 1
            team_2_players=event.team_2_players   # List of players for team 2
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        return db_event  
    except Exception as e:
        db.rollback()  
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")

# GET endpoint to retrieve all matches
@app.get("/matches/", response_model=List[CricketMatchEventOut])
def get_matches(db: Session = Depends(get_db)):
    return db.query(CricketMatchEvent).all()






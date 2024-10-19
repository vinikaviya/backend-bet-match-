from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import OperationalError
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

# Database URL
DATABASE_URL = "mysql+pymysql://root:vinikaviya2003@localhost:3306/betting"

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
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

# Call the function to create the database
create_database_if_not_exists()

# Table Definition
class User(Base):
    __tablename__ = "user_register"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    date_of_birth = Column(String(20))
    email = Column(String(100), unique=True)  # Ensure unique email
    hashed_password = Column(String(255))  # Store hashed password
    phone = Column(String(15))

# Create the table
Base.metadata.create_all(bind=engine)

# Pydantic models for request bodies
class UserRequest(BaseModel):
    full_name: str
    date_of_birth: str
    email: str
    password: str
    phone: str

class UserLogin(BaseModel):
    email: str
    password: str

# FastAPI instance
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Helper function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Endpoint to add user data
@app.post("/user/")
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

# Endpoint for user login
@app.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Query the database for the user
    db_user = db.query(User).filter(User.email == user.email).first()
    
    # Check if user exists and password matches
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "full_name": db_user.full_name,
            "email": db_user.email,
            "phone": db_user.phone,
        },
    }


#----------------------- ADMIN LOGIN----------------------


class AdminRequest(BaseModel):
    email: str
    password: str



class Admin(Base):
    __tablename__= "admin"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))


# Endpoint to add admin data
@app.post("/admin/")
def create_admin(admin: AdminRequest, db: Session = Depends(get_db)):
    try:
        # Check if the admin email already exists
        existing_admin = db.query(Admin).filter(Admin.email == admin.email).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Admin email is already registered")
        
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
    
    except Exception as e:
        print(f"Error creating admin: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating admin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AdminLogin(BaseModel):
    email: str
    password: str

# Endpoint for admin login
@app.post("/adminlogin/")
def admin_login(admin: AdminLogin, db: Session = Depends(get_db)):
    try:
        # Query the database for the admin
        db_admin = db.query(Admin).filter(Admin.email == admin.email).first()
        
        # Check if admin exists and password matches
        if not db_admin or not verify_password(admin.password, db_admin.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid admin credentials")

        return {
            "message": "Admin login successful",
            "admin": {
                "id": db_admin.id,
                "email": db_admin.email,
            },
        }
    except Exception as e:
        print(f"Error during admin login: {e}")
        raise HTTPException(status_code=500, detail="Invalid mail and password")






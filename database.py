from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

# Database URL
DATABASE_URL = "mysql+pymysql://root:vinikaviya2003@localhost:3306/betting"

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

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

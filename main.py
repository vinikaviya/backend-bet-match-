# main.py
from fastapi import FastAPI
from database import Base, engine
import user, admin, cricket

app = FastAPI()

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(user.router, prefix="/users")
app.include_router(admin.router, prefix="/admins")
app.include_router(cricket.router, prefix="/cricket")

from fastapi import FastAPI
from database import Base, engine
import user, admin, cricket,payment
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(user.router, prefix="/users")
app.include_router(admin.router, prefix="/admins")
app.include_router(cricket.router, prefix="/cricket")
app.include_router(payment.router, prefix="/payment")





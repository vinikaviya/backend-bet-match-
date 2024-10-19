from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Pydantic model for admin login
class AdminLogin(BaseModel):
    email: str
    password: str

# Hardcoded admin credentials
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

# Endpoint for admin login
@app.post("/adminlogin/")
def admin_login(admin: AdminLogin):
    # Validate admin credentials
    if admin.email != ADMIN_EMAIL or admin.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    return {
        "message": "Admin login successful",
        "admin": {
            "email": admin.email,
        },
    }

# To run the app, save this code in a file (e.g., admin_login.py) and run:
# uvicorn admin_login:app --reload

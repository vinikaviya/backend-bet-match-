
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, Base
from sqlalchemy import Column, Integer, String
import qrcode
import io
from fastapi.responses import StreamingResponse, JSONResponse


router = APIRouter()


class Payment(Base):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    mobile = Column(String(15), nullable=False)
    country = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)

# Pydantic model for receiving payment data in the specified order
class PaymentRequest(BaseModel):
    email: str
    name: str
    mobile: str
    country: str
    state: str
    city: str
    amount: int

# Pydantic response model with QR code URL
class PaymentResponse(BaseModel):
    message: str
    payment: PaymentRequest
    qr_code_url: str

# UPI ID for generating payment QR code
UPI_ID = "riyanajency123@oksbi"

# Payment creation route
@router.post("/payments/", response_model=PaymentResponse)
def create_payment(payment: PaymentRequest, db: Session = Depends(get_db)):
    # Create a new Payment instance for the database
    db_payment = Payment(
        email=payment.email,
        name=payment.name,
        mobile=payment.mobile,
        country=payment.country,
        state=payment.state,
        city=payment.city,
        amount=payment.amount
    )
    
    # Add the payment to the database
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Generate the QR code URL
    qr_code_url = f"/payments/qr_code?amount={db_payment.amount}"

    # Return JSON response with payment details and QR code URL
    return PaymentResponse(
        message=f"Payment of {payment.amount} received successfully.",
        payment=payment,
        qr_code_url=qr_code_url
    )

# Endpoint to generate QR code for the payment
@router.get("/payments/qr_code", responses={200: {"content": {"image/png": {}}}})
def get_qr_code(amount: int = Query(..., description="The amount for the payment")):

    # QR code data with UPI ID and amount
    qr_data = f"upi://pay?pa={UPI_ID}&am={amount}"
    qr_img = qrcode.make(qr_data)

    # Save QR code to a byte array
    img_byte_arr = io.BytesIO()
    qr_img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    
    # Stream the QR code image as a response
    return StreamingResponse(img_byte_arr, media_type="image/png")



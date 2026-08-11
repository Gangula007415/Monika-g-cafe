from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models

router = APIRouter(prefix="/customers", tags=["Customer Management"])

@router.get("/")
def list_customers(db: Session = Depends(get_db)):
    # Return every user with the Customer role (role_id 4, per register.html)
    customers = db.query(models.User).filter(models.User.role_id == 4).all()

    return [
        {
            "user_id": c.user_id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "phone_profile": c.phone_profile,
        }
        for c in customers
    ]

@router.get("/{customer_id}/history")
def get_order_history(customer_id: int, db: Session = Depends(get_db)):
    # Explicitly fetch orders and return them as a list of dictionaries
    orders = db.query(models.Order).filter(models.Order.customer_id == customer_id).all()
    
    return [
        {
            "order_id": o.order_id,
            "order_type": o.order_type,
            "order_status": o.order_status,
            "created_at": o.created_at.isoformat() if o.created_at else None
        }
        for o in orders
    ]

@router.get("/{customer_id}/loyalty")
def get_loyalty_points(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.User).filter(models.User.user_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
        
    return {
        "customer_id": customer_id,
        "loyalty_points": customer.loyalty_points
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas

router = APIRouter(prefix="/billing", tags=["Billing & Payments"])

@router.post("/")
def generate_bill(bill_data: schemas.BillCreate, db: Session = Depends(get_db)):
    # 1. Check if the order even exists first!
    order = db.query(models.Order).filter(models.Order.order_id == bill_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order ID not found in the system.")

    # 2. Prevent duplicate bills
    existing_bill = db.query(models.Bill).filter(models.Bill.order_id == bill_data.order_id).first()
    if existing_bill:
        raise HTTPException(status_code=400, detail="Bill already generated for this order")
        
    new_bill = models.Bill(**bill_data.model_dump(), payment_status="Paid")
    db.add(new_bill)
    
    # 3. Safely award loyalty points
    if order.customer_id:
        customer = db.query(models.User).filter(models.User.user_id == order.customer_id).first()
        if customer:
            customer.loyalty_points += int(bill_data.total_amount // 10)
            
    db.commit()
    return {"message": "Payment captured and bill generated", "bill_id": new_bill.bill_id}

@router.get("/{order_id}")
def get_bill_by_order(order_id: int, db: Session = Depends(get_db)):
    bill = db.query(models.Bill).filter(models.Bill.order_id == order_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill
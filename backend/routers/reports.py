from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("/sales-summary")
def get_sales_summary(db: Session = Depends(get_db)):
    total_orders = db.query(func.count(models.Order.order_id)).scalar()
    total_revenue = db.query(func.sum(models.Bill.total_amount)).filter(models.Bill.payment_status == "Paid").scalar() or 0.0
    
    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue)
    }

@router.get("/top-items")
def get_top_selling_items(db: Session = Depends(get_db)):
    # Aggregates item sales count via bridge records
    top_items = db.query(
        models.MenuItem.name, 
        func.sum(models.OrderItem.quantity).label("total_sold")
    ).join(models.OrderItem).group_by(models.MenuItem.name).order_by(func.sum(models.OrderItem.quantity).desc()).limit(5).all()
    
    return [{"item_name": item[0], "total_sold": int(item[1])} for item in top_items]
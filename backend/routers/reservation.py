from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas

router = APIRouter(prefix="/reservations", tags=["Table Reservation System"])

@router.post("/")
def book_table(res: schemas.ReservationCreate, db: Session = Depends(get_db)):
    new_res = models.Reservation(**res.model_dump(), status="Pending")
    db.add(new_res)
    
    # Temporarily hold the cafe table layout state
    table = db.query(models.CafeTable).filter(models.CafeTable.table_id == res.table_id).first()
    if table:
        table.status = "Reserved"
        
    db.commit()
    return {"message": "Reservation submitted successfully", "reservation_id": new_res.reservation_id}

@router.get("/")
def get_all_reservations(db: Session = Depends(get_db)):
    return db.query(models.Reservation).all()
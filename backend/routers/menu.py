from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas

router = APIRouter(prefix="/menu", tags=["Menu Management"])

@router.get("/")
def get_menu(db: Session = Depends(get_db)):
    return db.query(models.MenuItem).all()

@router.post("/")
def add_menu_item(item: schemas.MenuItemSchema, db: Session = Depends(get_db)):
    db_item = models.MenuItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": "Item added successfully", "item_id": db_item.item_id}
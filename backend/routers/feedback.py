from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas

router = APIRouter(prefix="/feedback", tags=["Feedback & Reviews"])

@router.post("/")
def leave_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    db_feedback = models.Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    return {"message": "Thank you for your response feedback."}

@router.get("/")
def view_all_feedbacks(db: Session = Depends(get_db)):
    return db.query(models.Feedback).all()
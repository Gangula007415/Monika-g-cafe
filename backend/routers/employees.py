from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from backend.database import get_db
from backend import models, schemas

router = APIRouter(prefix="/employees", tags=["Employee Management"])

@router.post("/")
def create_employee_profile(emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Verify user exists before making an employee record
    user = db.query(models.User).filter(models.User.user_id == emp.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User Account ID not found in system.")

    existing_emp = db.query(models.Employee).filter(models.Employee.user_id == emp.user_id).first()
    if existing_emp:
        raise HTTPException(status_code=400, detail="An employee profile already exists for this User ID.")

    db_emp = models.Employee(**emp.model_dump())
    db.add(db_emp)
    db.commit()
    return {"message": "Employee profile initialized successfully", "employee_id": db_emp.employee_id}

@router.get("/")
def list_employees(db: Session = Depends(get_db)):
    # Returns raw employee fields joined with user details for names/emails
    results = db.query(
        models.Employee.employee_id,
        models.Employee.user_id,
        models.Employee.salary,
        models.Employee.hire_date,
        models.Employee.status,
        models.User.first_name,
        models.User.last_name,
        models.User.email
    ).join(models.User, models.Employee.user_id == models.User.user_id).all()
    
    return [
        {
            "employee_id": r[0],
            "user_id": r[1],
            "salary": float(r[2]),
            "hire_date": str(r[3]),
            "status": r[4],
            "name": f"{r[5]} {r[6]}",
            "email": r[7]
        } for r in results
    ]

@router.put("/{employee_id}")
def update_employee_profile(employee_id: int, emp_data: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")
    
    employee.salary = emp_data.salary
    employee.hire_date = emp_data.hire_date
    db.commit()
    return {"message": "Employee metrics updated successfully"}
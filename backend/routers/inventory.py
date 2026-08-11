from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory Management"]
)


# ==========================
# SUPPLIER MANAGEMENT
# ==========================

@router.post("/suppliers")
def create_supplier(
    supplier_data: schemas.SupplierCreate,
    db: Session = Depends(get_db)
):
    supplier = models.Supplier(
        supplier_name=supplier_data.supplier_name,
        contact_name=supplier_data.contact_name,
        phone=supplier_data.phone,
        email=supplier_data.email
    )

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return {
        "message": "Supplier created successfully",
        "supplier_id": supplier.supplier_id
    }


@router.get("/suppliers")
def get_suppliers(
    db: Session = Depends(get_db)
):
    return db.query(models.Supplier).all()



# ==========================
# INGREDIENT MANAGEMENT
# ==========================

@router.post("/ingredients")
def add_ingredient(
    ingredient_data: schemas.IngredientCreate,
    db: Session = Depends(get_db)
):

    if ingredient_data.supplier_id is not None:

        supplier = db.query(models.Supplier).filter(
            models.Supplier.supplier_id == ingredient_data.supplier_id
        ).first()

        if not supplier:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )


    ingredient = models.Ingredient(
        name=ingredient_data.name,
        stock_level=ingredient_data.stock_level,
        unit=ingredient_data.unit,
        low_stock_threshold=ingredient_data.low_stock_threshold,
        supplier_id=ingredient_data.supplier_id
    )

    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    return {
        "message": "Ingredient added successfully",
        "ingredient_id": ingredient.ingredient_id
    }



@router.get("/ingredients")
def get_ingredients(
    db: Session = Depends(get_db)
):
    return db.query(models.Ingredient).all()



@router.get("/ingredients/{ingredient_id}")
def get_single_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db)
):

    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.ingredient_id == ingredient_id
    ).first()

    if not ingredient:
        raise HTTPException(
            status_code=404,
            detail="Ingredient not found"
        )

    return ingredient



@router.put("/ingredients/{ingredient_id}")
def update_ingredient(
    ingredient_id: int,
    ingredient_data: schemas.IngredientCreate,
    db: Session = Depends(get_db)
):

    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.ingredient_id == ingredient_id
    ).first()

    if not ingredient:
        raise HTTPException(
            status_code=404,
            detail="Ingredient not found"
        )


    if ingredient_data.supplier_id:

        supplier = db.query(models.Supplier).filter(
            models.Supplier.supplier_id == ingredient_data.supplier_id
        ).first()

        if not supplier:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )


    ingredient.name = ingredient_data.name
    ingredient.stock_level = ingredient_data.stock_level
    ingredient.unit = ingredient_data.unit
    ingredient.low_stock_threshold = ingredient_data.low_stock_threshold
    ingredient.supplier_id = ingredient_data.supplier_id

    db.commit()
    db.refresh(ingredient)

    return {
        "message": "Ingredient updated successfully"
    }



@router.delete("/ingredients/{ingredient_id}")
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db)
):

    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.ingredient_id == ingredient_id
    ).first()

    if not ingredient:
        raise HTTPException(
            status_code=404,
            detail="Ingredient not found"
        )

    db.delete(ingredient)
    db.commit()

    return {
        "message": "Ingredient deleted successfully"
    }



# ==========================
# INVENTORY ALERTS
# ==========================

@router.get("/alerts")
def get_inventory_alerts(
    db: Session = Depends(get_db)
):
    ingredients = db.query(models.Ingredient).filter(
        models.Ingredient.stock_level <= models.Ingredient.low_stock_threshold
    ).all()

    return ingredients



# ==========================
# RESTOCK INGREDIENT
# ==========================

@router.patch("/ingredients/{ingredient_id}/restock")
def restock_ingredient(
    ingredient_id: int,
    amount: int,
    db: Session = Depends(get_db)
):

    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.ingredient_id == ingredient_id
    ).first()

    if not ingredient:
        raise HTTPException(
            status_code=404,
            detail="Ingredient not found"
        )


    ingredient.stock_level += amount

    db.commit()
    db.refresh(ingredient)

    return {
        "message": "Ingredient restocked successfully",
        "ingredient_id": ingredient.ingredient_id,
        "new_stock_level": ingredient.stock_level
    }
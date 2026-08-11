from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas

router = APIRouter(
    prefix="/orders",
    tags=["Order Management"]
)


@router.post("/", response_model=dict)
def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(get_db)
):

    # Check customer exists
    if order_data.customer_id:
        customer = db.query(models.User).filter(
            models.User.user_id == order_data.customer_id
        ).first()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )


    # Check table exists
    if order_data.table_id:
        table = db.query(models.CafeTable).filter(
            models.CafeTable.table_id == order_data.table_id
        ).first()

        if not table:
            raise HTTPException(
                status_code=404,
                detail="Table not found"
            )


    # Create Order
    new_order = models.Order(
        customer_id=order_data.customer_id,
        table_id=order_data.table_id,
        order_type=order_data.order_type,
        order_status="Pending"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)


    # Create Order Items
    for item in order_data.items:

        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.item_id == item.item_id
        ).first()

        if not menu_item:
            raise HTTPException(
                status_code=404,
                detail=f"Menu item {item.item_id} not found"
            )


        order_item = models.OrderItem(
            order_id=new_order.order_id,
            item_id=item.item_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )

        db.add(order_item)


        # Inventory deduction
        recipes = db.query(
            models.MenuItemIngredient
        ).filter(
            models.MenuItemIngredient.item_id == item.item_id
        ).all()


        for recipe in recipes:

            ingredient = db.query(
                models.Ingredient
            ).filter(
                models.Ingredient.ingredient_id == recipe.ingredient_id
            ).first()


            if ingredient:
                ingredient.stock_level -= (
                    recipe.quantity_required * item.quantity
                )


    db.commit()


    return {
        "message": "Order placed successfully",
        "order_id": new_order.order_id
    }



@router.get("/")
def list_orders(
    db: Session = Depends(get_db)
):

    return db.query(models.Order).all()



@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):

    order = db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()


    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


    return order



@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    order = db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()


    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


    order.order_status = status
    db.commit()


    return {
        "message": f"Order status updated to {status}"
    }



@router.patch("/{order_id}/status")
def update_order_status_patch(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):

    status_map = {
        "pending": "Pending",
        "preparing": "Preparing",
        "completed": "Completed",
        "cancelled": "Cancelled"
    }


    normalized_status = status_map.get(
        new_status.lower()
    )


    if not normalized_status:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )


    order = db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()


    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


    order.order_status = normalized_status

    db.commit()


    return {
        "message": f"Order #{order_id} status updated to {normalized_status}"
    }



@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db)
):

    order = db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()


    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


    db.delete(order)
    db.commit()


    return {
        "message": "Order deleted successfully"
    }
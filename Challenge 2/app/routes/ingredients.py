"""
ingredients.py
Provides FastAPI routes to manage ingredients (add, update, delete, list).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import SessionLocal
from app.db import models

router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add")
def add_ingredient(
    ingredient_name: str,
    quantity: Optional[float] = None,
    unit: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Add a new ingredient to the database.
    """
    new_ingredient = models.Ingredient(
        ingredient_name=ingredient_name,
        quantity=quantity,
        unit=unit
    )
    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)
    return {
        "message": "Ingredient added successfully",
        "ingredient_id": new_ingredient.ingredient_id
    }

@router.put("/update/{ingredient_id}")
def update_ingredient(
    ingredient_id: int,
    quantity: Optional[float] = None,
    unit: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update an existing ingredient's quantity or unit.
    """
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.ingredient_id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    if quantity is not None:
        ingredient.quantity = quantity
    if unit is not None:
        ingredient.unit = unit

    db.commit()
    db.refresh(ingredient)
    return {"message": f"Ingredient {ingredient_id} updated"}

@router.delete("/{ingredient_id}")
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove an ingredient from the database.
    """
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.ingredient_id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    db.delete(ingredient)
    db.commit()
    return {"message": f"Ingredient {ingredient_id} deleted"}

@router.get("/", response_model=List[dict])
def list_ingredients(db: Session = Depends(get_db)):
    """
    List all ingredients available at home.
    """
    ingredients = db.query(models.Ingredient).all()
    return [
        {
            "ingredient_id": ing.ingredient_id,
            "ingredient_name": ing.ingredient_name,
            "quantity": ing.quantity,
            "unit": ing.unit
        }
        for ing in ingredients
    ]

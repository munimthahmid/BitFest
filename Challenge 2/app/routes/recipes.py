"""
recipes.py
Provides FastAPI routes to manage (add, retrieve, update, delete) recipes
and also includes an endpoint to input new favorite recipes from raw text.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
import os

from app.db.database import SessionLocal
from app.db import models
from app.utils.parse_recipes import parse_recipe_block, insert_parsed_recipes_to_db

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add")
def add_recipe(
    recipe_title: str,
    ingredients_required: str,
    instructions: str,
    taste_profile: Optional[str] = None,
    reviews: Optional[str] = None,
    cuisine_type: Optional[str] = None,
    preparation_time: Optional[int] = None,
    additional_tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Add a new recipe (structured JSON input).
    """
    new_recipe = models.Recipe(
        recipe_title=recipe_title,
        ingredients_required=ingredients_required,
        instructions=instructions,
        taste_profile=taste_profile,
        reviews=reviews,
        cuisine_type=cuisine_type,
        preparation_time=preparation_time,
        additional_tags=additional_tags
    )
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return {"message": "Recipe added", "recipe_id": new_recipe.recipe_id}

@router.post("/upload_text")
def add_favorite_recipe_text(
    raw_text: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Accepts a raw text snippet (e.g., "Title: ...\nIngredients: ...\nInstructions: ..."),
    appends it to `my_fav_recipes.txt`, then parses it and stores in the DB.
    """
    # 1) Append the raw_text to my_fav_recipes.txt (include a separator).
    file_path = "my_fav_recipes.txt"
    with open(file_path, "a", encoding="utf-8") as f:
        # Separate from previous entries using a line with '---'
        f.write("\n---\n")
        f.write(raw_text.strip())
        f.write("\n")

    # 2) Parse just this snippet (we can do block-based parsing).
    parsed_recipe = parse_recipe_block(raw_text)
    # 3) Insert the parsed recipe(s) into DB
    insert_parsed_recipes_to_db([parsed_recipe], db)

    return {"message": "Recipe text appended and inserted into DB"}

@router.get("/", response_model=List[dict])
def get_recipes(
    taste_profile: Optional[str] = Query(None),
    cuisine_type: Optional[str] = Query(None),
    max_prep_time: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieve recipes with optional filters:
     - taste_profile
     - cuisine_type
     - max_prep_time
     - free-text search in title, instructions, or ingredients_required
    """
    query = db.query(models.Recipe)

    if taste_profile:
        query = query.filter(models.Recipe.taste_profile == taste_profile)

    if cuisine_type:
        query = query.filter(models.Recipe.cuisine_type == cuisine_type)

    if max_prep_time is not None:
        query = query.filter(models.Recipe.preparation_time <= max_prep_time)

    if search:
        # naive LIKE search across three fields
        pattern = f"%{search}%"
        query = query.filter(
            (models.Recipe.recipe_title.like(pattern)) |
            (models.Recipe.instructions.like(pattern)) |
            (models.Recipe.ingredients_required.like(pattern))
        )

    results = query.all()

    # Convert to dict
    return [
        {
            "recipe_id": r.recipe_id,
            "recipe_title": r.recipe_title,
            "ingredients_required": r.ingredients_required,
            "instructions": r.instructions,
            "taste_profile": r.taste_profile,
            "reviews": r.reviews,
            "cuisine_type": r.cuisine_type,
            "preparation_time": r.preparation_time,
            "additional_tags": r.additional_tags
        }
        for r in results
    ]

@router.get("/{recipe_id}")
def get_recipe_by_id(recipe_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single recipe by ID.
    """
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {
        "recipe_id": recipe.recipe_id,
        "recipe_title": recipe.recipe_title,
        "ingredients_required": recipe.ingredients_required,
        "instructions": recipe.instructions,
        "taste_profile": recipe.taste_profile,
        "reviews": recipe.reviews,
        "cuisine_type": recipe.cuisine_type,
        "preparation_time": recipe.preparation_time,
        "additional_tags": recipe.additional_tags
    }

@router.put("/update/{recipe_id}")
def update_recipe(
    recipe_id: int,
    recipe_title: Optional[str] = None,
    ingredients_required: Optional[str] = None,
    instructions: Optional[str] = None,
    taste_profile: Optional[str] = None,
    reviews: Optional[str] = None,
    cuisine_type: Optional[str] = None,
    preparation_time: Optional[int] = None,
    additional_tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update an existing recipe with provided fields.
    """
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if recipe_title is not None:
        recipe.recipe_title = recipe_title
    if ingredients_required is not None:
        recipe.ingredients_required = ingredients_required
    if instructions is not None:
        recipe.instructions = instructions
    if taste_profile is not None:
        recipe.taste_profile = taste_profile
    if reviews is not None:
        recipe.reviews = reviews
    if cuisine_type is not None:
        recipe.cuisine_type = cuisine_type
    if preparation_time is not None:
        recipe.preparation_time = preparation_time
    if additional_tags is not None:
        recipe.additional_tags = additional_tags

    db.commit()
    db.refresh(recipe)
    return {"message": f"Recipe {recipe_id} updated"}

@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """
    Delete a recipe by its ID.
    """
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)
    db.commit()
    return {"message": f"Recipe {recipe_id} deleted"}

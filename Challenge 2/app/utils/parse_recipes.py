"""
parse_recipes.py
Utilities for parsing recipes from a text file or raw text blocks.
"""

import os
from app.db.database import Base, engine
from app.db import models
from sqlalchemy.orm import Session

# Automatically create tables (if they don't exist) when this module is imported or used
Base.metadata.create_all(bind=engine)

def parse_recipe_block(raw_block: str) -> dict:
    """
    Parses a single recipe text block (e.g., "Title: ...\nIngredients: ...\nInstructions: ...")
    and returns a dict with the discovered fields.
    Fields: Title, Ingredients, Instructions, Taste, Reviews, Cuisine, PrepTime, AdditionalTags
    """
    lines = raw_block.strip().split("\n")
    recipe_data = {
        "Title": None,
        "Ingredients": None,
        "Instructions": None,
        "Taste": None,
        "Reviews": None,
        "Cuisine": None,
        "PrepTime": None,
        "AdditionalTags": None
    }

    for line in lines:
        # e.g. "Title: Chocolate Cake"
        lower_line = line.lower().strip()
        if lower_line.startswith("title:"):
            recipe_data["Title"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("ingredients:"):
            recipe_data["Ingredients"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("instructions:"):
            recipe_data["Instructions"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("taste:"):
            recipe_data["Taste"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("reviews:"):
            recipe_data["Reviews"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("cuisine:"):
            recipe_data["Cuisine"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("preptime:"):
            recipe_data["PrepTime"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("additionaltags:"):
            recipe_data["AdditionalTags"] = line.split(":", 1)[1].strip()

    return recipe_data

def insert_parsed_recipes_to_db(parsed_recipes: list, db: Session):
    """
    Inserts a list of parsed recipe dictionaries into the DB, converting types if needed.
    """
    for rd in parsed_recipes:
        prep_time_int = None
        if rd["PrepTime"]:
            try:
                prep_time_int = int(rd["PrepTime"])
            except ValueError:
                prep_time_int = None

        new_recipe = models.Recipe(
            recipe_title=rd["Title"] or "Untitled",
            ingredients_required=rd["Ingredients"] or "",
            instructions=rd["Instructions"] or "",
            taste_profile=rd["Taste"] or "",
            reviews=rd["Reviews"] or "",
            cuisine_type=rd["Cuisine"] or "",
            preparation_time=prep_time_int,
            additional_tags=rd["AdditionalTags"] or ""
        )
        db.add(new_recipe)
    db.commit()

def parse_recipe_file(filepath: str) -> list:
    """
    Parses an entire recipe file (my_fav_recipes.txt) that may contain multiple recipes
    separated by '---'.
    Returns a list of recipe dictionaries.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} does not exist.")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by '---' to separate each recipe block
    blocks = content.split("---")
    parsed_data = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        recipe_dict = parse_recipe_block(block)
        parsed_data.append(recipe_dict)

    return parsed_data

def insert_recipes_from_file(filepath: str):
    """
    Reads the file, parses it, and inserts everything into the database (fresh session).
    """
    db = Session(bind=engine)
    try:
        parsed_list = parse_recipe_file(filepath)
        insert_parsed_recipes_to_db(parsed_list, db)
        print(f"Inserted {len(parsed_list)} recipes from {filepath}")
    finally:
        db.close()

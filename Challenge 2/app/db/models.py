"""
models.py
Defines the SQLAlchemy models for both Ingredients and Recipes.
"""

from sqlalchemy import Column, Integer, String, Text, Float
from .database import Base

class Ingredient(Base):
    """
    Stores each available ingredient Mofa has at home.
    """
    __tablename__ = "ingredients"

    ingredient_id = Column(Integer, primary_key=True, index=True)
    ingredient_name = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=True)  # If you want to store numeric amounts
    unit = Column(String(50), nullable=True) # e.g., 'cups', 'grams', 'kg'

    def __repr__(self):
        return f"<Ingredient(id={self.ingredient_id}, name={self.ingredient_name}, quantity={self.quantity}, unit={self.unit})>"

class Recipe(Base):
    """
    Stores text-based recipes with fields to enable easier retrieval.
    """
    __tablename__ = "recipes"

    recipe_id = Column(Integer, primary_key=True, index=True)
    recipe_title = Column(String(255), nullable=False)
    ingredients_required = Column(Text, nullable=True)  # e.g., 'Flour; Sugar; Eggs'
    instructions = Column(Text, nullable=True)          # Full instructions or steps
    taste_profile = Column(String(50), nullable=True)    # e.g., 'sweet', 'savory'
    reviews = Column(Text, nullable=True)                # Could store plain text or JSON
    cuisine_type = Column(String(50), nullable=True)     # e.g., 'Italian', 'Chinese'
    preparation_time = Column(Integer, nullable=True)    # in minutes
    additional_tags = Column(Text, nullable=True)        # e.g., 'chocolate, dessert'

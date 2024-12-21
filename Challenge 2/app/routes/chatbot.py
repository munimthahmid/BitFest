"""
chatbot.py
Integrates an LLM-based chatbot (Gemini Flash) that recommends recipes
based on user preferences AND the ingredients available at home.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import google.generativeai as genai

from app.db.database import SessionLocal
from app.db.models import Recipe, Ingredient

router = APIRouter(prefix="/chat", tags=["Chatbot"])

# Configure Gemini

genai.configure(api_key="AIzaSyCRJeYVTghti6NmF4XzOYP5W6WF1CKEV6g")
model = genai.GenerativeModel("gemini-1.5-flash")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    user_message: str

@router.post("/")
def chat_with_gemini(request: ChatRequest, db: Session = Depends(get_db)):
    """
    1) Parse user's preference from user_message.
    2) Filter recipes that match preference (e.g., sweet).
    3) Check the user's available ingredients (ingredients table).
    4) Recommend only those recipes that can be made with the user's current ingredients.
    5) Send final context + user message to Gemini for a natural language response.
    """

    user_message = request.user_message.lower().strip()

    # Example: check if user wants "sweet" or "savory" or "spicy"
    taste_profile = None
    if "sweet" in user_message:
        taste_profile = "sweet"
    elif "savory" in user_message:
        taste_profile = "savory"
    elif "spicy" in user_message:
        taste_profile = "spicy"
    # You can expand this logic for more advanced parsing.

    # 1) Retrieve all recipes if taste_profile not found, else filter
    recipe_query = db.query(Recipe)
    if taste_profile:
        recipe_query = recipe_query.filter(Recipe.taste_profile == taste_profile)

    candidate_recipes = recipe_query.all()

    # 2) Retrieve all available ingredients
    available_ingredients = db.query(Ingredient).all()
    # Store them in a dictionary for easier checking: { "sugar": 2.0, "flour": 1.5, ... }
    # We'll do a name-based approach (case-insensitive).
    ingredient_dict = {}
    for ing in available_ingredients:
        ing_name_lower = ing.ingredient_name.lower()
        ingredient_dict[ing_name_lower] = ingredient_dict.get(ing_name_lower, 0) + (ing.quantity or 0)

    # 3) Filter candidate_recipes to those that can be made with available ingredients.
    #    Our 'ingredients_required' is a text field (e.g. "Flour; Sugar; Eggs").
    #    We'll do a basic approach: check if all required ingredient names appear in the user’s pantry.
    #    For a robust approach, parse amounts, units, etc. But let's keep it simple.

    def can_make_recipe(recipe: Recipe) -> bool:
        if not recipe.ingredients_required.strip():
            return True  # no ingredients needed? trivial
        required_ingredients = [x.strip().lower() for x in recipe.ingredients_required.split(";") if x.strip()]
        for req in required_ingredients:
            if req not in ingredient_dict:
                return False
        return True

    feasible_recipes = [r for r in candidate_recipes if can_make_recipe(r)]

    # 4) Build a context string describing feasible recipes
    if not feasible_recipes:
        context = "No recipes fully match your available ingredients for this preference.\n"
    else:
        context = "Based on your available ingredients, here are suitable recipes:\n"
        for r in feasible_recipes:
            context += f" - {r.recipe_title} (prep time: {r.preparation_time} min)\n"

    # 5) Construct a final prompt for Gemini
    system_prompt = (
        "You are Mofa's Kitchen Buddy, an AI assistant that helps users cook. "
        "You have data about their available ingredients and can recommend only feasible recipes. "
        "If no feasible recipe is found, politely say so.\n\n"
    )
    user_section = f"User says: {request.user_message}\n\n"
    context_section = f"Context about recipes:\n{context}\n\n"
    assistant_prompt = "Please respond with the best suggestions or apologies if none match."

    final_prompt = system_prompt + user_section + context_section + assistant_prompt

    try:
        response = model.generate_content(final_prompt)
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")

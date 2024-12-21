"""
main.py
FastAPI entry point: creates the app, initializes DB, loads existing recipes (if any),
and includes the routes for ingredients and recipes.
"""

from fastapi import FastAPI
from app.db.database import Base, engine
from app.routes import ingredients, recipes,chatbot
from app.utils.parse_recipes import insert_recipes_from_file

app = FastAPI(
    title="Mofa’s Kitchen Buddy - Text-based Recipe Retrieval",
    description="APIs for managing ingredients and text-based recipes.",
    version="1.0.0"
)

# Create DB tables if they don't already exist
Base.metadata.create_all(bind=engine)

# On startup, parse the existing my_fav_recipes.txt (if present) and load them into DB
@app.on_event("startup")
def load_initial_recipes():
    filepath = "my_fav_recipes.txt"
    try:
        insert_recipes_from_file(filepath)
        print(f"Startup: Loaded recipes from {filepath}")
    except FileNotFoundError:
        print(f"No {filepath} file found, skipping initial recipe loading.")

# Register our routers
app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(chatbot.router)

@app.get("/")
def root():
    return {"message": "Welcome to Mofa's Kitchen Buddy (Text-based)! Use /docs for API documentation."}

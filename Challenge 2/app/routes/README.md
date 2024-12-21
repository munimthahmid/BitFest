README for Mofa’s Kitchen Buddy

This document describes the entire setup, configuration, usage, and examples for Mofa’s Kitchen Buddy—a backend system that manages ingredients, retrieves recipes (from text files or images via OCR), and integrates with a chatbot (powered by Google’s Gemini Flash) to suggest recipes based on what’s available at home.

---------------------------------------------------------------------------
TABLE OF CONTENTS

1) Overview
2) Features
3) Installation
4) Setup & Configuration
5) Running the Server
6) Usage
   6.1) Ingredient Management
   6.2) Recipe Management (Text-Based)
   6.3) OCR Integration (Optional)
   6.4) Chatbot Integration (Gemini Flash)
7) Examples
   7.1) Add a Sweet Recipe
   7.2) Add the Required Ingredients
   7.3) Chat: “I want something sweet”
8) Extending & Customizing
9) License

---------------------------------------------------------------------------

1) OVERVIEW

Mofa’s Kitchen Buddy is designed to handle:
- Ingredients: Add, update, delete items in Mofa’s kitchen.
- Recipes: Parse from a large text file (my_fav_recipes.txt), upload from raw text, or optionally from images (OCR).
- Chatbot: A Large Language Model integration (using Gemini Flash from Google) that:
  • Understands user preferences (e.g., “I want something sweet”).
  • Checks the available ingredients in the kitchen.
  • Recommends only those recipes that can be prepared with those ingredients.

---------------------------------------------------------------------------

2) FEATURES

- Database Schema:
  • Ingredients table (name, quantity, unit).
  • Recipes table (title, ingredients_required, taste_profile, reviews, cuisine_type, preparation_time, additional_tags).

- Ingredient Management API:
  • Add new ingredients (POST /ingredients/add)
  • Update existing ingredients (PUT /ingredients/update/{id})
  • Delete ingredients (DELETE /ingredients/{id})
  • List all ingredients (GET /ingredients)

- Recipe Retrieval:
  • Load/parse from my_fav_recipes.txt
  • Add recipes from raw text (appending to the file)
  • Add recipes from images (OCR)
  • Search/filter with optional parameters (taste_profile, cuisine_type, max_prep_time, search)

- Chatbot Integration:
  • Uses Gemini Flash (google-generativeai library)
  • Recommends recipes that fit user preferences AND match the available ingredients.

---------------------------------------------------------------------------

3) INSTALLATION

1. Clone or download this repository.
2. Install dependencies by running:
   pip install -r requirements.txt
3. (Optional) If using OCR, ensure Tesseract is installed on your system. For instance, on Ubuntu:
   sudo apt-get update
   sudo apt-get install tesseract-ocr

---------------------------------------------------------------------------

4) SETUP & CONFIGURATION

1. Database
   By default, the system uses SQLite (test.db) in the project root.
   If you wish to use another DB (e.g., PostgreSQL), modify SQLALCHEMY_DATABASE_URL in app/db/database.py.

2. Gemini Flash API Key
   Obtain your Gemini API Key from Google.
   Set it as an environment variable. For example:
   export GEMINI_API_KEY="YOUR_GEMINI_KEY"

3. my_fav_recipes.txt (Optional)
   If you have an existing file with recipes, place it at the project root.
   On startup, the system parses this file (delimited by '---') and loads the recipes into test.db.

---------------------------------------------------------------------------

5) RUNNING THE SERVER

Use uvicorn to launch the FastAPI server:

uvicorn app.main:app --reload

After it starts, the API is accessible at:
http://127.0.0.1:8000

API Documentation:
• Swagger UI: http://127.0.0.1:8000/docs
• ReDoc: http://127.0.0.1:8000/redoc

---------------------------------------------------------------------------

6) USAGE

6.1) Ingredient Management

Endpoints:
• POST /ingredients/add
  Example JSON body:
  {
    "ingredient_name": "Flour",
    "quantity": 2,
    "unit": "cups"
  }

• PUT /ingredients/update/{ingredient_id}
  Example JSON body:
  {
    "quantity": 3,
    "unit": "cups"
  }

• DELETE /ingredients/{ingredient_id}
  Deletes an ingredient by ID.

• GET /ingredients
  Lists all ingredients.

6.2) Recipe Management (Text-Based)

• Load from my_fav_recipes.txt
  On startup, this file is parsed (each recipe separated by '---') and inserted into the DB.

• Add from Raw Text
  POST /recipes/upload_text
  Example JSON:
  {
    "raw_text": "Title: Pancakes\nIngredients: Flour; Milk; Eggs\nInstructions: Mix and fry.\nTaste: sweet\nReviews: 5 stars\nCuisine: Breakfast\nPrepTime: 15\nAdditionalTags: fluffy"
  }
  This text is appended to my_fav_recipes.txt, then parsed and inserted into the DB.

• Add via Structured JSON
  POST /recipes/add
  Example JSON:
  {
    "recipe_title": "Waffles",
    "ingredients_required": "Flour; Milk; Eggs; Sugar",
    "instructions": "Mix the batter. Cook in waffle maker.",
    "taste_profile": "sweet",
    "reviews": "Crispy on the outside!",
    "cuisine_type": "Breakfast",
    "preparation_time": 20,
    "additional_tags": "dessert"
  }

• Retrieve/Search Recipes
  GET /recipes
  Supports query parameters: taste_profile, cuisine_type, max_prep_time, search

• GET /recipes/{recipe_id}
  Retrieve one recipe by ID.

• PUT /recipes/update/{id}
  Update any fields of a recipe.

• DELETE /recipes/{id}
  Remove a recipe.

6.3) OCR Integration (Optional)

• If you plan to accept images, you must have parse_ocr.py (pytesseract + Pillow).
• Endpoint: POST /recipes/upload_image
  Accepts an image (e.g., .png, .jpg) via multipart form:
  curl -X POST "http://127.0.0.1:8000/recipes/upload_image" -F "file=@/path/to/recipe_screenshot.png"
  Tesseract extracts text -> appended to my_fav_recipes.txt -> parsed -> inserted into DB.

6.4) Chatbot Integration (Gemini Flash)

• Endpoint: POST /chat

Flow:
1) Parse the user’s message (for instance: "I want something sweet").
2) Filter recipes that match (taste_profile = sweet).
3) Cross-check them with the user’s available ingredients (ingredients table).
4) Provide only feasible recipes to Gemini Flash as context.
5) Return the LLM-generated text to the user.

Example request:
curl -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d '{"user_message": "I want something sweet"}'

Sample response:
{
  "reply": "Here are some sweet recipes you can try..."
}
(Exact text depends on Gemini’s generative output.)

---------------------------------------------------------------------------

7) EXAMPLES

7.1) Add a Sweet Recipe

curl -X POST http://127.0.0.1:8000/recipes/add \
-H "Content-Type: application/json" \
-d '{
  "recipe_title": "Chocolate Cake",
  "ingredients_required": "Flour; Sugar; Eggs; Cocoa",
  "instructions": "Mix ingredients, bake at 350F for 30 mins.",
  "taste_profile": "sweet",
  "reviews": "Family favorite",
  "cuisine_type": "Dessert",
  "preparation_time": 45,
  "additional_tags": "cake, chocolate"
}'

Response:
{"message": "Recipe added", "recipe_id": 1}

7.2) Add the Required Ingredients

Add each ingredient with POST /ingredients/add

Example:
curl -X POST http://127.0.0.1:8000/ingredients/add \
-H "Content-Type: application/json" \
-d '{
  "ingredient_name": "Flour",
  "quantity": 2,
  "unit": "cups"
}'

Repeat similarly for "Sugar", "Eggs", "Cocoa," etc.

7.3) Chat: “I want something sweet”

Once you have:
• A sweet recipe: Chocolate Cake
• The required ingredients: Flour, Sugar, Eggs, Cocoa

curl -X POST http://127.0.0.1:8000/chat \
-H "Content-Type: application/json" \
-d '{
  "user_message": "I want something sweet"
}'

Possible Response:
{
  "reply": "You can make a Chocolate Cake! Here are the steps..."
}

Exact text depends on Gemini’s generative output, but it should confirm that “Chocolate Cake” is feasible.

---------------------------------------------------------------------------

8) EXTENDING & CUSTOMIZING

• Chat History
  If you want multi-turn conversations, store user and assistant messages in a DB or session.

• Better Ingredient Matching
  Instead of a simple name check, parse amounts and units to confirm adequate supply.

• Advanced NLP
  Use a library to parse user queries for time constraints, specific cuisines, or dietary restrictions.

• Advanced Search
  Consider full-text search or vector embeddings for more sophisticated recipe retrieval.

---------------------------------------------------------------------------

9) LICENSE

This project is provided under your preferred license terms. Insert license text here.

Enjoy cooking with Mofa’s Kitchen Buddy!


```md
# Mofa’s Kitchen Buddy

A **backend system** that helps Mofa manage his ingredients, **retrieve recipes** (from text or images via OCR), and **interact with a chatbot** (powered by Google’s Gemini Flash) to **suggest recipes** based on **what's available at home**.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Setup \& Configuration](#setup--configuration)
- [Running the Server](#running-the-server)
- [Usage](#usage)
  - [1. Ingredient Management](#1-ingredient-management)
  - [2. Recipe Management (Text-Based)](#2-recipe-management-text-based)
  - [3. OCR Integration (Optional)](#3-ocr-integration-optional)
  - [4. Chatbot Integration (Gemini Flash)](#4-chatbot-integration-gemini-flash)
- [Examples](#examples)
  - [A) Add a Sweet Recipe](#a-add-a-sweet-recipe)
  - [B) Add the Required-Ingredients](#b-add-the-required-ingredients)
  - [C) Chat: "I want something sweet"](#c-chat-i-want-something-sweet)
- [Extending \& Customizing](#extending--customizing)
- [License](#license)

---

## Overview

**Mofa’s Kitchen Buddy** is designed to handle:

1. **Ingredients**: Add/update/delete items in Mofa’s kitchen.  
2. **Recipes**: Parse from a large text file (`my_fav_recipes.txt`), upload from raw text, or optionally from **images** (OCR).  
3. **Chatbot**: A Large Language Model integration (using **Gemini Flash** from Google) that:
   - Understands user preferences (e.g., “I want something sweet”).
   - Checks the **available ingredients** in the kitchen.
   - Recommends only those recipes that can be prepared with those ingredients.

---

## Features

- **Database Schema**  
  - `Ingredients` table (name, quantity, unit).  
  - `Recipes` table (title, ingredients_required, taste_profile, etc.).

- **Ingredient Management API**  
  - Add new ingredients (`POST /ingredients/add`).  
  - Update existing ingredients (`PUT /ingredients/update/{id}`).  
  - Delete ingredients (`DELETE /ingredients/{id}`).  
  - List all ingredients (`GET /ingredients`).

- **Recipe Retrieval**  
  - Load/parse from `my_fav_recipes.txt`.  
  - Add recipes from **raw text** (appending to the file).  
  - Add recipes from **image** (OCR).  
  - Search/filter with optional parameters (`taste_profile`, `cuisine_type`, `max_prep_time`, `search`).

- **Chatbot Integration**  
  - Uses **Gemini Flash** via the `google-generativeai` library.  
  - Recommends recipes that **fit user preferences** **and** **match** the **available ingredients**.

---

## Installation

1. **Clone or download** this repository.  
2. **Install dependencies** by running:
   ```bash
   pip install -r requirements.txt
   ```
3. *(Optional)* If using OCR, ensure **Tesseract** is installed on your system. For instance, on Ubuntu:
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   ```

---

## Setup & Configuration

1. **Database**  
   - By default, the system uses **SQLite** (`test.db`) in the project root.  
   - If you wish to use another DB (e.g., PostgreSQL), modify `SQLALCHEMY_DATABASE_URL` in `app/db/database.py`.

2. **Gemini Flash API Key**  
   - Obtain your **Gemini API Key** from Google.  
   - Set it as an environment variable:
     ```bash
     export GEMINI_API_KEY="YOUR_GEMINI_KEY"
     ```

3. **`my_fav_recipes.txt`** (Optional)  
   - If you have an existing file with recipes, place it at the project root.  
   - On startup, the system parses this file (delimited by `---`) and loads the recipes into `test.db`.

---

## Running the Server

Launch the FastAPI server with **uvicorn**:

```bash
uvicorn app.main:app --reload
```

The API is accessible at:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)

**API Documentation**:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Usage

### 1. Ingredient Management

**Endpoints**:

- **POST** `/ingredients/add`  
  Example JSON body:
  ```json
  {
    "ingredient_name": "Flour",
    "quantity": 2,
    "unit": "cups"
  }
  ```
- **PUT** `/ingredients/update/{ingredient_id}`  
  Example JSON body:
  ```json
  {
    "quantity": 3,
    "unit": "cups"
  }
  ```
- **DELETE** `/ingredients/{ingredient_id}`  
  Deletes an ingredient by ID.

- **GET** `/ingredients`  
  Lists all ingredients.

### 2. Recipe Management (Text-Based)

- **Load from `my_fav_recipes.txt`**  
  On startup, this file is parsed (each recipe separated by `---`) and inserted into the DB.

- **Add from Raw Text**  
  **POST** `/recipes/upload_text`  
  ```json
  {
    "raw_text": "Title: Pancakes\nIngredients: Flour; Milk; Eggs\nInstructions: Mix and fry.\nTaste: sweet\nReviews: 5 stars\nCuisine: Breakfast\nPrepTime: 15\nAdditionalTags: fluffy"
  }
  ```
  This text is appended to `my_fav_recipes.txt`, then parsed and inserted into the DB.

- **Add via Structured JSON**  
  **POST** `/recipes/add`  
  ```json
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
  ```

- **Retrieve/Search Recipes**  
  **GET** `/recipes`  
  Supports query parameters:
  - `taste_profile=...`
  - `cuisine_type=...`
  - `max_prep_time=...`
  - `search=...` (keyword search on title, instructions, and ingredients)

- **GET** `/recipes/{recipe_id}`  
  Retrieve one recipe by ID.

- **PUT** `/recipes/update/{id}`  
  Update any fields of a recipe.

- **DELETE** `/recipes/{id}`  
  Remove a recipe.

### 3. OCR Integration (Optional)

- **File**: `app/utils/parse_ocr.py` uses **pytesseract** + **Pillow**.  
- **Endpoint**: **POST** `/recipes/upload_image`  
  Accepts an image (e.g., `.png`, `.jpg`) via **multipart form**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/recipes/upload_image" \
       -F "file=@/path/to/recipe_screenshot.png"
  ```
  **Tesseract** extracts text → appended to `my_fav_recipes.txt` → parsed → inserted into DB.

### 4. Chatbot Integration (Gemini Flash)

- **Endpoint**: **POST** `/chat`

**Flow**:
1. Parse the user’s message (e.g., “I want something sweet”).  
2. Filter recipes that match (e.g., `taste_profile=sweet`).  
3. Cross-check them with the **user’s available ingredients** from the `ingredients` table.  
4. Provide only feasible recipes to **Gemini Flash** as context.  
5. Return the LLM’s generated text to the user.

**Example request**:
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"user_message": "I want something sweet"}'
```

**Sample response**:
```json
{
  "reply": "Here are some sweet recipes you can try..."
}
```
(Exact text depends on Gemini’s generative output.)

---

## Examples

### A) Add a Sweet Recipe

```bash
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
```
**Result**:
```json
{"message": "Recipe added", "recipe_id": 1}
```

### B) Add the Required-Ingredients

Add each ingredient with **POST** `/ingredients/add`:

```bash
# Add Flour
curl -X POST http://127.0.0.1:8000/ingredients/add \
     -H "Content-Type: application/json" \
     -d '{
       "ingredient_name": "Flour",
       "quantity": 2,
       "unit": "cups"
     }'

# Add Sugar
curl -X POST http://127.0.0.1:8000/ingredients/add \
     -H "Content-Type: application/json" \
     -d '{
       "ingredient_name": "Sugar",
       "quantity": 1,
       "unit": "cup"
     }'

# Add Eggs
curl -X POST http://127.0.0.1:8000/ingredients/add \
     -H "Content-Type: application/json" \
     -d '{
       "ingredient_name": "Eggs",
       "quantity": 2
     }'

# Add Cocoa
curl -X POST http://127.0.0.1:8000/ingredients/add \
     -H "Content-Type: application/json" \
     -d '{
       "ingredient_name": "Cocoa",
       "quantity": 1,
       "unit": "tablespoon"
     }'
```

### C) Chat: "I want something sweet"

Now you have:
- A **sweet** recipe: **Chocolate Cake**.
- All required ingredients: Flour, Sugar, Eggs, Cocoa.

```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{
       "user_message": "I want something sweet"
     }'
```

**Response** (example):
```json
{
  "reply": "You can make a Chocolate Cake! Here are the steps..."
}
```
The exact text depends on Gemini’s generative output, but it should reference **Chocolate Cake** as feasible given your available ingredients.

---

## Extending & Customizing

- **Chat History**  
  - Store previous user and assistant messages for multi-turn conversations.

- **Better Ingredient Matching**  
  - Parse amounts/units rather than just name matching (currently we do a simple name check).

- **Advanced NLP**  
  - Use a library to parse user queries for time constraints, cuisine, dietary restrictions, etc.

- **Advanced Search**  
  - Consider full-text search or vector embeddings for more sophisticated recipe retrieval.

---

## License

This project is provided under your preferred license terms. (Insert license text here.)

**Enjoy cooking with Mofa’s Kitchen Buddy!**
```
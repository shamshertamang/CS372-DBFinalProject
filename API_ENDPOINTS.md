## API Endpoint Documentation

This document provides a reference for all HTTP endpoints defined in the application Blueprints (`auth.py` and `views.py`). AI was used to generate this API endpoint documentation and verified by me. Each entry covers:

* **Method** & **URL**
* **Auth**: whether login is required
* **Description**
* **Request parameters** (path, form, file uploads)
* **Behavior / Response**

### Table of Contents

1. [Authentication](#authentication)
2. [Home](#home)
3. [Recipes](#recipes)
4. [Meals](#meals)
5. [Meal Plans](#meal-plans)
6. [Profile & Account](#profile--account)

### Authentication

| Method    | URL        | Auth | Description                                                                                                                                        |
| --------- | ---------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET, POST | `/login`   | No   | Show login form (GET) or authenticate credentials (POST). Redirects to home on success, flashes error on failure.                                  |
| GET       | `/logout`  | Yes  | Log out current user and redirect to login page.                                                                                                   |
| GET, POST | `/sign-up` | No   | Show signup form (GET) or create new user (POST). Validates email format, username uniqueness, password match/length. Logs in new user on success. |


### Home

#### `GET /`

* **Auth:** Yes
* **Description:** Render dashboard listing current user’s recipes, meals, and meal plans.
* **Response:** HTML (`home.html`) with context: `user`, `recipes`, `meals`, `meal_plans`.

### Recipes

| Method   | URL                   | Auth | Description                       |
| -------- | --------------------- | ---- | --------------------------------- |
| GET      | `/add-recipe`         | Yes  | Show "Create Recipe" form         |
| POST     | `/add-recipe`         | Yes  | Create a new recipe               |
| GET      | `/edit-recipe/<id>`   | Yes  | Show form to edit a recipe        |
| POST     | `/edit-recipe/<id>`   | Yes  | Update an existing recipe         |
| GET      | `/recipe/<id>`        | Yes  | View recipe details               |
| GET,POST | `/delete-recipe/<id>` | Yes  | Delete a recipe and redirect home |

#### `POST /add-recipe` & `POST /edit-recipe/<id>`

* **Content-Type:** `multipart/form-data`
* **Form Fields:**

  * `name` (string, required)
  * `origin` (string)
  * `difficulty_level` (int 1–5)
  * `preparation_steps` (string, comma-separated, required)
  * `preparation_time` (minutes)
  * `cooking_time` (minutes)
  * `serving` (int, required)
  * `source` (string)
  * `ingredients` (string, comma-separated, required)
  * `photo` (file, optional)
* **Behavior:** Validate inputs, parse values, insert/update `Recipe` and `RecipeIngredient` records, flash success or error, and redirect.


### Meals

| Method | URL                 | Auth | Description                        |
| ------ | ------------------- | ---- | ---------------------------------- |
| GET    | `/add-meal`         | Yes  | Show "Create Meal" form            |
| POST   | `/add-meal`         | Yes  | Create a new meal                  |
| GET    | `/meal/<id>`        | Yes  | View meal details                  |
| GET    | `/edit-meal/<id>`   | Yes  | Show form to edit an existing meal |
| POST   | `/edit-meal/<id>`   | Yes  | Update an existing meal            |
| POST   | `/delete-meal/<id>` | Yes  | Delete a meal and redirect to home |

#### `POST /add-meal` & `POST /edit-meal/<id>`

* **Form Fields:**

  * `meal_title` (string, required)
  * `meal_time` (string, required)
  * `recipe_ids` (array of ints via multi-select, required)
* **Behavior:** Check title uniqueness, manage `Meal` and junction table entries, flash messages, and redirect.


### Meal Plans

| Method | URL                      | Auth | Description                                  |
| ------ | ------------------------ | ---- | -------------------------------------------- |
| GET    | `/add-meal-plan`         | Yes  | Show "Create Meal Plan" form                 |
| POST   | `/add-meal-plan`         | Yes  | Create a new meal plan with schedule entries |
| GET    | `/view-meal-plan/<id>`   | Yes  | View meal plan and its scheduled meals       |
| GET    | `/edit-meal-plan/<id>`   | Yes  | Show form to edit an existing meal plan      |
| POST   | `/edit-meal-plan/<id>`   | Yes  | Update an existing meal plan                 |
| POST   | `/delete-meal-plan/<id>` | Yes  | Delete a meal plan and its schedule entries  |

#### `POST /add-meal-plan` & `POST /edit-meal-plan/<id>`

* **Form Fields:**

  * `plan_title` (string, required)
  * `start_date` (YYYY-MM-DD, required)
  * `end_date` (YYYY-MM-DD, required)
  * `goals` (string, optional)
  * `meal_ids` (array of ints, required)
  * `schedule_<meal_id>` (YYYY-MM-DD HH\:MM for each selected meal)
* **Behavior:** Validate date range and title uniqueness, manage `MealPlan` and schedule entries, flash messages, and redirect to plan view.


### Profile & Account

| Method | URL               | Auth | Description                                           |
| ------ | ----------------- | ---- | ----------------------------------------------------- |
| GET    | `/profile`        | Yes  | Show user profile page                                |
| POST   | `/profile`        | Yes  | Update user profile (incl. photo upload)              |
| POST   | `/delete-account` | Yes  | Delete user account and all related data, then logout |

#### `POST /profile`

* **Content-Type:** `multipart/form-data`
* **Form Fields:**

  * `profile_picture` (file, optional)
  * `user_name` (string)
  * `email` (string, unique)
  * `dietary_preferences` (string, comma-separated)
  * `cooking_level` (int 1–5)
  * `allergies` (string, comma-separated)
* **Behavior:** Validate inputs, parse lists, update `User` record, flash messages, and redirect.

#### `POST /delete-account`

* **Behavior:** Delete `User` and cascade delete related recipes, meals, and plans; call `logout_user()`, flash confirmation, and redirect to login.

*End of API Endpoint Documentation.*

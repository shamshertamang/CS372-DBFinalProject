# database.py

import sqlite3
import json
import os
from pathlib import Path
from .models import User


DB_PATH = Path("instance/database.db")
DDL_PATH = Path("website/sql/ddl.sql")
DML_PATH = Path("website/sql/dml.sql")


def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_database(db_path=DB_PATH):
    if not db_path.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = get_db_connection()
        cursor = conn.cursor()

        for script in (DDL_PATH, DML_PATH):
            with script.open(encoding="utf-8") as f:
                cursor.executescript(f.read())
        conn.commit()
        print("Database created and populated successfully")

######################################
# ----------- User Related -----------
######################################

# base query for get_user
_BASE_USER_WITH_JSON = """
    SELECT u.id, u.user_name, u.name, u.email, u.password, u.cooking_level, u.photo_data,
        COALESCE(
            (SELECT json_group_array(preference)
                FROM user_dietary_preference
                WHERE user_id = u.id), '[]') AS dietary_preferences,
        COALESCE(
            (SELECT json_group_array(allergy)
                FROM user_allergy
                WHERE user_id = u.id), '[]') AS allergies
    FROM users AS u
"""

# get_user by email
def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    user_row = cursor.execute(
        _BASE_USER_WITH_JSON + " WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return User(user_row) if user_row else None

# get_user by user_name
def get_user_by_username(user_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    user_row = cursor.execute(
        _BASE_USER_WITH_JSON + " WHERE user_name = ?", (user_name,)
    ).fetchone()
    conn.close()
    return User(user_row) if user_row else None

# get_user by id
def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    user_row = cursor.execute(
        _BASE_USER_WITH_JSON + " WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return User(user_row) if user_row else None

def create_user(email, name, user_name, password, photo_data, cooking_level=1,
                dietary_preferences = None, allergies = None):
    """
    - dietary_preferences: python list of strings
    - allergies: python list of strings
    """

    dietary_preferences = dietary_preferences or []
    allergies = allergies or []

    conn = get_db_connection()
    cursor = conn.cursor()

    # input data in user table
    cursor.execute('''
        INSERT INTO users (email, user_name, password, cooking_level, photo_data)
        VALUES (?, ?, ?, ?, ?)
    ''', (email, user_name, password, cooking_level, photo_data))
    user_id = cursor.lastrowid

    # input data in dietary_preferences
    for pref in dietary_preferences:
        cursor.execute("""
            INSERT INTO user_dietary_preference (user_id, preference) 
            VALUES (?, ?)""", (user_id, pref)
        )

    # input data in allergy
    for allergy in allergies:
        cursor.execute("""
        INSERT INTO user_allergy (user_id, allergy) 
        VALUES (?,?)""", (user_id, allergy))
    conn.commit()
    conn.close()
    user_row = get_user_by_email(email)
    return User(user_row)

def update_user_profile(user_id, email, user_name, photo_data, cooking_level, dietary_preferences, allergies):

    conn = get_db_connection()
    cursor = conn.cursor()

    dietary_preferences = dietary_preferences or []
    allergies = allergies or []

    try:
        # update user
        cursor.execute("""
            Update users 
            set user_name = ?, email = ?, cooking_level = ?, photo_data = ?
            where id = ?
        """, (user_name, email, cooking_level, photo_data, user_id))

        cursor.execute(
            "DELETE FROM user_dietary_preference WHERE user_id = ?",
            (user_id,)
        )
        for pref in dietary_preferences:
            cursor.execute("""
                        INSERT INTO user_dietary_preference (user_id, preference)
                        VALUES (?, ?)
                    """, (user_id, pref))

        cursor.execute(
            "DELETE FROM user_allergy WHERE user_id = ?",
            (user_id,)
        )
        for allergy in allergies:
            cursor.execute("""
                        INSERT INTO user_allergy (user_id, allergy)
                        VALUES (?, ?)
                    """, (user_id, allergy))
        conn.commit()
    except Exception as e:
        print("⚠️ Update failed, rolling back:", e)
        conn.rollback()
    finally:
        conn.close()
        return get_user_by_id(user_id)

def delete_user_by_id(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

#############################################
# ----------- Ingredient Related -----------#
#############################################

def create_ingredient(user_id: int,
                      name: str,
                      store: str = None,
                      unit: str = None,
                      seasonal_availability: str = None) -> int:
    """
    Inserts a new ingredient into the Ingredient table for a given user.

    Parameters:
        user_id (int): ID of the user adding the ingredient.
        name (str): Unique name of the ingredient.
        store (str, optional): Preferred store name.
        unit (str, optional): Unit of measurement (e.g., 'g', 'cup').
        nutritional_label (dict, optional): Nutritional info stored as JSON.
        alternative_stores (list, optional): Alternative store names as JSON list.
        common_substitutes (list, optional): Common substitutes as JSON list.
        seasonal_availability (str, optional): Seasonality info.

    Returns:
        int: ID of the newly created ingredient.

    Raises:
        sqlite3.IntegrityError: If the ingredient name already exists for this user.
    """
    # Serialize JSON fields if provided

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO Ingredient (
            user_id, name, store, unit, seasonal_availability
        ) VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            name,
            store,
            unit,
            seasonal_availability
        )
    )
    conn.commit()
    ingredient_id = cursor.lastrowid
    conn.close()
    return ingredient_id

def get_ingredients(user_id: int, name_query: str):
    """
    Return the ingredient for a given user whose name matches name_query.

    Uses a case‐insensitive LIKE search so you can pass part of the name.

    Parameters:
      user_id     – the ID of the user who owns the ingredients
      name_query  – the ingredient name or fragment to look for

    Returns:
      A list of sqlite3.Row objects, each representing one ingredient.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Use LOWER() on both sides for case‐insensitive matching,
    # and wrap name_query in % for partial matches.
    sql = """
        SELECT *
        FROM ingredient
        WHERE user_id = ? AND LOWER(name) LIKE LOWER(?)
    """
    pattern = f"%{name_query.strip()}%"
    rows = cursor.execute(sql, (user_id, pattern)).fetchone()
    conn.close()
    return rows

####################################################
# ----------- Recipe Ingredient Related -----------#
####################################################

def create_recipe_ingredient(recipe_id: int,
                             ingredient_id: int,
                             quantity: str = None,
                             unit: str = None) -> None:
    """
    Creates an entry in the RecipeIngredient table linking a recipe and an ingredient,
    with optional quantity and unit.

    Parameters:
        recipe_id (int): ID of the recipe.
        ingredient_id (int): ID of the ingredient.
        quantity (str, optional): Quantity used (e.g., '2').
        unit (str, optional): Unit of the quantity (e.g., 'cups').

    Raises:
        ValueError: If the link already exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''
            INSERT INTO recipe_ingredient (
                recipe_id, ingredient_id, quantity, unit
            ) VALUES (?, ?, ?, ?)
            ''', (
                recipe_id,
                ingredient_id,
                quantity,
                unit
            )
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(
            f"Link between recipe {recipe_id} and ingredient {ingredient_id} already exists."
        ) from e
    finally:
        conn.close()

def get_recipe_ingredients(recipe_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    ingredients = cursor.execute('''
            SELECT ingredient.name
            FROM ingredient
            JOIN recipe_ingredient ON ingredient.id = recipe_ingredient.ingredient_id
            WHERE recipe_ingredient.recipe_id = ?
        ''', (recipe_id,)).fetchall()

    conn.close()
    return ingredients


def delete_recipe_ingredient(recipe_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recipe_ingredient WHERE recipe_id = ?', (recipe_id,))
    conn.commit()
    conn.close()

#########################################
# ----------- Recipe Related -----------#
#########################################
def create_recipe(user_id: int, name: str, preparation_steps: list, preparation_time: str, cooking_time: str,
                  origin: str = 'To be known', difficulty: int = 1, serving_size: int = 1,
                  source: str = 'Unknown', photo_data: list = None) -> int:

    """
     Insert a new recipe into the Recipe table.

     Parameters:
     - user_id: ID of the user creating the recipe
     - name: Unique recipe name
     - origin: Recipe origin text
     - difficulty: Difficulty level (1-5)
     - preparation_steps: List of preparation steps
     - preparation_time: Prep time in HH:MM:SS format
     - cooking_time: Cooking time in HH:MM:SS format
     - serving_size: Number of servings
     - source: Recipe source (e.g., 'AI' or 'self')
     - photos: List of up to 4 photo URLs or identifiers -- update-- only 1 photo per recipe now
     """

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO recipe (
                        user_id, name, origin, difficulty,
                        preparation_time, cooking_time,
                        serving_size, source, photo
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    (user_id, name, origin, difficulty, preparation_time, cooking_time, serving_size, source,
        photo_data)
    )
    recipe_id = cursor.lastrowid
    conn.commit()
    conn.close()

    for idx, step in enumerate(preparation_steps, start=1):
                insert_recipe_steps(recipe_id, idx, step)

    return recipe_id



def get_all_recipes(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    recipes = cursor.execute("""
        SELECT r.id, r.name, r.origin, r.photo
        FROM recipe AS r
        WHERE r.user_id = ?
        ORDER BY r.id
    """, (user_id,)).fetchall()
    conn.close()
    return recipes

def get_recipe(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    recipe = cursor.execute('SELECT * FROM recipe WHERE id = ?', (recipe_id,)).fetchone()
    conn.close()
    return recipe

def get_recipe_by_name(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    recipe_id = cursor.execute('SELECT id FROM recipe WHERE name = ?', (name,)).fetchone()
    conn.close()
    if recipe_id:
        return recipe_id[0]
    return None

def update_recipe(name, origin, difficulty, preparation_steps, preparation_time, cooking_time,
                  serving_size, source, photo_data:bytes, recipe_id):

    # need to handle ingredient update
    conn = get_db_connection()
    cursor = conn.cursor()

    if photo_data is not None:
            # user uploaded a new image → overwrite
            cursor.execute('''
                UPDATE recipe
                SET name = ?, origin = ?, difficulty = ?, preparation_time = ?, cooking_time = ?, 
                    serving_size = ?, source = ?, photo = ?
                WHERE id = ?
            ''', (name, origin, difficulty, preparation_time, cooking_time, serving_size, source,
                  photo_data, recipe_id)
            )
    else:
        # no new image → leave photo untouched
        cursor.execute('''
            UPDATE recipe
                SET name = ?, origin = ?, difficulty = ?, preparation_time = ?, cooking_time = ?, 
                    serving_size = ?, source = ?
                WHERE id = ?
            ''', (name, origin, difficulty, preparation_time, cooking_time, serving_size,
            source, recipe_id)
        )
    conn.commit()

    delete_recipe_steps(recipe_id)

    for idx, step in enumerate(preparation_steps, start=1):
        insert_recipe_steps(recipe_id, idx, step)

    conn.close()

def insert_recipe_steps(recipe_id, step_number, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipe_step (recipe_id, step_number, description)
        VALUES (?, ?, ?)""", (recipe_id, step_number, description))
    conn.commit()
    conn.close()

def delete_recipe_steps(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        Delete FROM recipe_step where recipe_id = ?""", (recipe_id,))
    conn.commit()
    conn.close()

def get_recipe_steps(recipe_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT description
          FROM recipe_step
         WHERE recipe_id = ?
         ORDER BY step_number
    """, (recipe_id,)).fetchall()
    conn.close()
    return [r['description'] for r in rows]

def get_recipe_in_meal(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("""
        Select r.id, r.name, r.origin, r.photo, r.difficulty, r.cooking_time, r.serving_size, r.source
        FROM recipe AS r
        Join meal_recipe AS mr ON r.id = mr.recipe_id
        WHERE mr.meal_id = ?
    """, (meal_id,)).fetchall()
    conn.close()
    return rows

def get_recipe_ids_for_meal(meal_id: int) -> list[int]:
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT recipe_id FROM meal_recipe WHERE meal_id = ?",
        (meal_id,)
    ).fetchall()
    conn.close()
    return [r["recipe_id"] for r in rows]

def delete_recipes_from_meal(meal_id: int) -> None:
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM meal_recipe WHERE meal_id = ?",
        (meal_id,)
    )
    conn.commit()
    conn.close()

def delete_recipe_from_meal_recipe(meal_id: int, recipe_id:int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM meal_recipe WHERE meal_id = ? and recipe_id = ?
    """, (meal_id, recipe_id))
    conn.commit()
    conn.close()

def add_recipe_to_meal(meal_id: int, recipe_id: int) -> None:
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO meal_recipe (meal_id, recipe_id) VALUES (?, ?)",
        (meal_id, recipe_id)
    )
    conn.commit()
    conn.close()

#########################################
# ----------- Meals Related -----------#
#########################################

def create_meal(user_id: int, meal_title: str, recipe_ids: list[int], meal_time: str) -> int:
    """
    Creates a new meal for a user, with a list of recipe IDs, meal time, and scheduled datetime.

    Parameters:
        user_id (int): ID of the user creating the meal.
        meal_title(str): The title of the meal.
        recipe_ids (list): List of recipe IDs included in the meal.
        meal_time (str): The time of the meal, e.g., "Breakfast", "Lunch", "Dinner".
        scheduled_datetime (str): The scheduled date and time for the meal ("YYYY-MM-DD HH:MM:SS").

    Returns:
        int: ID of the newly created meal.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(''' 
            INSERT INTO Meal (user_id, meal_title, meal_time)
            VALUES (?, ?, ?)
        ''', (user_id, meal_title, meal_time))
    # cursor.execute('''
    #     INSERT INTO Meal (recipe_ids, user_id, meal_title, meal_time, scheduled_datetime)
    #     VALUES (?, ?, ?, ?, ?)
    # ''', (recipe_ids_json, user_id, meal_title, meal_time, scheduled_datetime))

    conn.commit()
    meal_id = cursor.lastrowid
    conn.close()

    for rid in recipe_ids:
        add_recipe_to_meal(meal_id, rid)

    return meal_id


def delete_meal(meal_id: int) -> None:
    """
    Deletes a meal by its ID.

    Parameters:
        meal_id (int): ID of the meal to be deleted.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Meal WHERE meal_id = ?', (meal_id,))
    conn.commit()
    conn.close()

def update_meal(meal_id: int,
                recipe_ids: list = None,
                meal_time: str = None,
                meal_title: str = None,
                # , scheduled_datetime: str = None
                ) -> None:
    """
    Updates a meal with new information such as recipes, meal time, or scheduled datetime.

    Parameters:
        meal_id (int): ID of the meal to be updated.
        recipe_ids (list, optional): Updated list of recipe IDs for the meal.
        meal_time (str, optional): Updated time of the meal (e.g., "Breakfast", "Lunch", "Dinner").
        scheduled_datetime (str, optional): Updated scheduled datetime for the meal ("YYYY-MM-DD HH:MM:SS").
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Set the fields to be updated (only update the ones that are not None)
    updates = []
    params = []

    if meal_title is not None:
        updates.append("meal_title = ?")
        params.append(meal_title)

    if recipe_ids is not None:
        updates.append("recipe_ids = ?")
        params.append(json.dumps(recipe_ids))  # Store recipe IDs as a JSON array

    if meal_time is not None:
        updates.append("meal_time = ?")
        params.append(meal_time)

    # if scheduled_datetime is not None:
    #     updates.append("scheduled_datetime = ?")
    #     params.append(scheduled_datetime)

    # Combine the update fields and parameters
    set_clause = ", ".join(updates)
    params.append(meal_id)  # Always append the meal_id as the last parameter

    cursor.execute(f'''
        UPDATE Meal
        SET {set_clause}
        WHERE meal_id = ?
    ''', tuple(params))

    conn.commit()
    conn.close()

def view_meal(meal_id: int):
    """
    Retrieves information about a specific meal by its ID.

    Parameters:
        meal_id (int): ID of the meal to view.

    Returns:
        dict: A dictionary representing the meal, or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    meal = cursor.execute('''
        SELECT * FROM Meal WHERE meal_id = ?
    ''', (meal_id,)).fetchone()

    conn.close()

    if meal:
        # Return the meal as a dictionary
        return dict(meal)

    return None

def get_all_meals(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select all rows from the Meal table
    meals = cursor.execute('SELECT * FROM meal where user_id = ?', (user_id,)).fetchall()

    conn.close()

    return meals

def get_meal(meal_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select all rows from the Meal table
    meal = cursor.execute("""
        SELECT * FROM Meal
        where meal_id = ?
    """, (meal_id,)).fetchone()

    conn.close()
    if not meal:
        return None

    return dict(meal)

def get_meal_by_name(user_id, meal_title: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select all rows from the Meal table
    meal = cursor.execute("""
        SELECT meal_id FROM Meal
        where user_id = ? and meal_title = ?
    """, (user_id, meal_title)).fetchone()

    conn.close()
    if not meal:
        return None

    return meal[0]

#########################################
# ----------- Meal Plan Related -----------#
#########################################
def create_meal_plan(user_id, title, start_date, end_date, goals):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO MealPlan
        (user_id, title, start_date, end_date, goals)
        VALUES (?, ?, ?, ?, ?)""", (user_id, title, start_date, end_date, goals)
    )

    conn.commit()
    plan_id = cursor.lastrowid
    conn.close()
    return plan_id

def create_meal_plan_with_schedule(user_id, title, start_date, end_date, goals, schedule_map):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO meal_plan (user_id, title, start_date, end_date, goals)
            VALUES (?, ?, ?, ?, ?)""", (user_id, title, start_date, end_date, goals)
        )
        plan_id = cursor.lastrowid

        for meal_id, sched in schedule_map.items():
            cursor.execute("""
            INSERT INTO meal_plan_meal(meal_plan_id, meal_id, scheduled_datetime)
            VALUES (?,?, ?)""", (plan_id, meal_id, sched))
        conn.commit()
        return plan_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def add_meal_to_plan(meal_plan_id, meal_id, scheduled_datetime):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO meal_plan_meal
        (meal_plan_id, meal_id, scheduled_datetime)
        VALUES (?, ?, ?)""", (meal_plan_id, meal_id, scheduled_datetime))
    conn.commit()
    conn.close()

def get_meal_plan(meal_plan_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    plan_row = cursor.execute(
        'SELECT * FROM meal_plan WHERE meal_plan_id = ? and user_id = ?',
        (meal_plan_id, user_id)
    ).fetchone()

    if not plan_row:
        return None
    return dict(plan_row)

def get_meal_plan_by_title(title):
    conn = get_db_connection()
    row = conn.execute(
      'SELECT meal_plan_id, user_id FROM MealPlan WHERE title = ?',
      (title,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_meal_plan_meals_and_schedules(meal_plan_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    row = cursor.execute("""
                SELECT m.meal_id, m.meal_title, ppm.scheduled_datetime
                FROM meal_plan_meal AS ppm
                JOIN meal AS m ON ppm.meal_id = m.meal_id
                WHERE ppm.meal_plan_id = ?
                ORDER BY ppm.scheduled_datetime
            """, (meal_plan_id,)).fetchall()

    return row

def get_meal_plan_by_user_and_title(user_id: int, title: str):
    conn = get_db_connection()
    row = conn.execute(
        'SELECT meal_plan_id FROM meal_plan WHERE user_id = ? AND title = ?',
        (user_id, title)
    ).fetchone()
    conn.close()
    return row['meal_plan_id'] if row else None

def delete_meal_plan_and_meal_plan_meals_by_id(meal_plan_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    # first remove all the schedule entries
    cur.execute('DELETE FROM meal_plan_meal WHERE meal_plan_id = ?', (meal_plan_id,))
    # then remove the plan itself
    cur.execute('DELETE FROM meal_plan WHERE meal_plan_id = ?', (meal_plan_id,))
    conn.commit()
    conn.close()

def get_all_meal_plans(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("""SELECT * FROM meal_plan where user_id = ?
        ORDER BY meal_plan_id""", (user_id,)).fetchall()
    conn.close()
    return rows

def update_meal_plan(title, start_date, end_date, goals, meal_plan_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
               UPDATE meal_plan
                  SET title = ?, start_date = ?, end_date = ?, goals = ?
                WHERE meal_plan_id = ?
           ''', (title, start_date, end_date, goals, meal_plan_id))

    conn.commit()
    conn.close()

def update_meal_plan_meal_schedule(meal_plan_id: int, meal_id: int, scheduled_datetime: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE meal_plan_meal
        SET scheduled_datetime = ?
        WHERE meal_plan_id = ? and meal_id = ?""",
        (scheduled_datetime, meal_plan_id, meal_id)
    )
    conn.commit()
    conn.close()

def delete_meal_plan_meal(meal_plan_id, meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meal_plan_meal WHERE meal_plan_id = ? and meal_id = ?',
                   (meal_plan_id, meal_id)
    )
    conn.commit()
    conn.close()


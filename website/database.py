# database.py

import sqlite3
import json
import os
from .models import User

def get_db_connection():
    conn = sqlite3.connect('instance/database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    # conn = sqlite3.connect('instance/database.db')
    # cursor = conn.cursor()
    #
    # cursor.execute("DROP TABLE IF EXISTS Meal")
    # cursor.execute("""
    #             CREATE TABLE Meal (
    #                 meal_id INTEGER PRIMARY KEY,
    #                 meal_title TEXT,
    #                 recipe_ids TEXT NOT NULL,  -- JSON array of Recipe IDs, stored as TEXT
    #                 user_id INTEGER NOT NULL,
    #                 meal_time TEXT,  -- E.g., "Breakfast", "Lunch", "Dinner"
    #                 scheduled_datetime TEXT, -- Store datetime as TEXT ("YYYY-MM-DD HH:MM:SS")
    #                 FOREIGN KEY (user_id) REFERENCES Users(user_id)
    #             );
    #         """)
    # conn.close()
    if not os.path.exists('instance/database.db'):
        conn = sqlite3.connect('instance/database.db')
        cursor = conn.cursor()

        # create Users
        cursor.execute('''
            CREATE TABLE Users (
                id INTEGER PRIMARY KEY,
                user_name TEXT UNIQUE NOT NULL,
                name TEXT,
                email TEXT UNIQUE NOT NULL,
                password TEXT,
                dietary_preferences TEXT,
                cooking_level INTEGER CHECK ( cooking_level >= 1 and cooking_level <= 5 ),
                allergies TEXT,
                subscription_status TEXT,
                photo_data blob
            )
        ''')

        # Create Ingredient table
        cursor.execute("""
            CREATE TABLE Ingredient (
                id   INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT UNIQUE NOT NULL,
                store TEXT,
                unit TEXT,
                nutritional_label JSON,
                alternative_stores JSON,
                common_substitutes JSON,
                seasonal_availability Text,
                Foreign Key (user_id) references Users(id)
            )
        """)

        # create recipe ingredients
        cursor.execute("""
            CREATE TABLE RecipeIngredient (
                recipe_id    INTEGER,
                ingredient_id INTEGER,
                quantity     TEXT,
                unit         TEXT,
                PRIMARY KEY (recipe_id, ingredient_id),
                FOREIGN KEY(recipe_id)    REFERENCES Recipe(id),
                FOREIGN KEY(ingredient_id) REFERENCES Ingredient(id)
            )
        """)

        # create recipe
        cursor.execute("""
            CREATE TABLE Recipe (
                id          INTEGER PRIMARY KEY,
                user_id     INTEGER,
                name TEXT UNIQUE,
                -- CollectionID INTEGER,
                origin TEXT,
                difficulty INTEGER CHECK ( Difficulty >= 1 and Difficulty <= 5 ),
                --Remindertimes Text,
                preparation_steps JSON,
                preparation_time time,
                cooking_time time,
                serving_size INTEGER,
                source TEXT, --_AI_or_self
                photos_json TEXT CHECK (
                    json_array_length(photos_json) <= 4
                ),
                FOREIGN KEY(user_id) REFERENCES User(id)
            )
        """)

        # create recipe_ingredient
        cursor.execute('''
            CREATE TABLE recipe_ingredient (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                ingredient_id INTEGER,
                FOREIGN KEY (recipe_id) REFERENCES recipe (id),
                FOREIGN KEY (ingredient_id) REFERENCES ingredient (id)
            )
        ''')

        # create meal
        cursor.execute("""
            CREATE TABLE Meal (
                meal_id INTEGER PRIMARY KEY,
                meal_title TEXT,
                recipe_ids TEXT NOT NULL,  -- JSON array of Recipe IDs, stored as TEXT
                user_id INTEGER NOT NULL,
                meal_time TEXT,  -- E.g., "Breakfast", "Lunch", "Dinner"
                scheduled_datetime TEXT, -- Store datetime as TEXT ("YYYY-MM-DD HH:MM:SS")
                FOREIGN KEY (user_id) REFERENCES Users(id)
            );
        """)

        # create meal plan
        cursor.execute("""
            CREATE TABLE MealPlan (
                meal_plan_id INTEGER PRIMARY KEY,
                title TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                start_date TEXT,  -- Store dates as TEXT (ISO format recommended: "YYYY-MM-DD")
                end_date TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            );
        """)

        # create meal plan meal
        cursor.execute("""
            CREATE TABLE MealPlanMeal (
            meal_plan_id INTEGER NOT NULL,
            meal_id INTEGER NOT NULL,
            PRIMARY KEY (meal_plan_id, meal_id),
            FOREIGN KEY (meal_plan_id) REFERENCES MealPlan(meal_plan_id),
            FOREIGN KEY (meal_id) REFERENCES Meal(meal_id)
        );
        """)

        # maybe pantry list

        # maybe shopping list

        conn.commit()
        conn.close()
        print('Database created successfully!')

######################################
# ----------- User Related -----------
######################################

def get_user_by_email(email):
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM Users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return User(user_row) if user_row else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM Users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return User(user_row) if user_row else None

def create_user(email, user_name, password_hash):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO Users (email, user_name, password, dietary_preferences, cooking_level, allergies, subscription_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (email, user_name, password_hash, json.dumps([]), 1, json.dumps([]), ''))
    conn.commit()
    user_row = conn.execute('SELECT * FROM Users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return User(user_row)

def update_user_profile(user_id, user_name, email, dietary_preferences, cooking_level, allergies, subscription_status, photo_data = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if photo_data is None:
            cursor.execute('''
                UPDATE Users
                SET user_name = ?, email = ?, dietary_preferences = ?, cooking_level = ?, allergies = ?, 
                    subscription_status = ?
                WHERE id = ?
            ''', (
                user_name,
                email,
                json.dumps(dietary_preferences),  # Only dietary_preferences as JSON
                int(cooking_level),
                json.dumps(allergies),  # allergies is stored as TEXT, no need for json.dumps
                subscription_status,
                user_id
            ))
        else :
            cursor.execute('''
                            UPDATE Users
                            SET user_name = ?, email = ?, dietary_preferences = ?, cooking_level = ?, allergies = ?, 
                                subscription_status = ?, photo_data = ?
                            WHERE id = ?
                        ''', (
                user_name,
                email,
                json.dumps(dietary_preferences),  # Only dietary_preferences as JSON
                int(cooking_level),
                json.dumps(allergies),  # allergies is stored as TEXT, no need for json.dumps
                subscription_status,
                photo_data,
                user_id
            ))
        conn.commit()
    except Exception as e:
        print("⚠️ Update failed, rolling back:", e)
        conn.rollback()
    finally:
        conn.close()

def delete_user_by_id(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

#############################################
# ----------- Ingredient Related -----------#
#############################################

def create_ingredient(user_id: int,
                      name: str,
                      store: str = None,
                      unit: str = None,
                      nutritional_label: dict = None,
                      alternative_stores: list = None,
                      common_substitutes: list = None,
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
    nutri_json = json.dumps(nutritional_label) if nutritional_label is not None else None
    alt_stores_json = json.dumps(alternative_stores) if alternative_stores is not None else None
    subs_json = json.dumps(common_substitutes) if common_substitutes is not None else None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO Ingredient (
            user_id, name, store, unit,
            nutritional_label, alternative_stores,
            common_substitutes, seasonal_availability
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            name,
            store,
            unit,
            nutri_json,
            alt_stores_json,
            subs_json,
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
          FROM Ingredient
         WHERE user_id = ?
           AND LOWER(name) LIKE LOWER(?)
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
            INSERT INTO RecipeIngredient (
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
                  source: str = 'Unknown', photos: list = None):

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
     - photos: List of up to 4 photo URLs or identifiers

     Raises:
     - ValueError: If difficulty or number of photos is out of allowed range
     """

    # Validate inputs
    if not (1 <= difficulty <= 5):
        raise ValueError("Difficulty must be between 1 and 5")
    if len(photos) > 4:
        raise ValueError("A maximum of 4 photos is allowed")

    photos_json = json.dumps(photos)
    steps_json = json.dumps(preparation_steps)

    conn = get_db_connection()
    cursor = conn.cursor()
    if photos_json is None:
        cursor.execute('''
                 INSERT INTO Recipe (
                     user_id, name, origin, difficulty, preparation_steps, preparation_time, cooking_time, 
                     serving_size, source, photos_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, name, origin, difficulty, steps_json, preparation_time,
                        cooking_time, serving_size, source, photos_json)
                )
    else:
        cursor.execute('''
             INSERT INTO Recipe (
                 user_id, name, origin, difficulty, preparation_steps, preparation_time, cooking_time, 
                 serving_size, source, photos_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, name, origin, difficulty, steps_json, preparation_time,
                        cooking_time, serving_size, source, photos_json)
            )
    conn.commit()
    conn.close()

    return cursor.lastrowid  # Return new recipe ID


def get_all_recipes():
    conn = get_db_connection()
    cursor = conn.cursor()
    recipes = cursor.execute('SELECT * FROM recipe').fetchall()
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
                  serving_size, source, photos, recipe_id):

    if not (1 <= difficulty <= 5):
        raise ValueError("difficulty must be between 1 and 5")
    if not isinstance(preparation_steps, list):
        raise ValueError("preparation_steps must be a list")

    # ensure at most 4 photos
    photos = list(photos)[:4]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE recipe
        SET name = ?, origin = ?, difficulty = ?, preparation_steps = ?, preparation_time = ?, 
        cooking_time = ?, serving_size = ?, source = ?, photos_json= ? 
        WHERE id = ?''', (name, origin, difficulty, json.dumps(preparation_steps),
                      preparation_time, cooking_time, serving_size, source, json.dumps(photos), recipe_id))
    conn.commit()
    conn.close()

#########################################
# ----------- Meals Related -----------#
#########################################

def create_meal(user_id: int, meal_title: str, recipe_ids: list, meal_time: str, scheduled_datetime: str) -> int:
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
    recipe_ids_json = json.dumps(recipe_ids)  # Store recipe IDs as a JSON array

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO Meal (recipe_ids, user_id, meal_title, meal_time, scheduled_datetime)
        VALUES (?, ?, ?, ?, ?)
    ''', (recipe_ids_json, user_id, meal_title, meal_time, scheduled_datetime))

    conn.commit()
    meal_id = cursor.lastrowid
    conn.close()

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

def update_meal(meal_id: int, recipe_ids: list = None, meal_time: str = None, scheduled_datetime: str = None) -> None:
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

    if recipe_ids is not None:
        updates.append("recipe_ids = ?")
        params.append(json.dumps(recipe_ids))  # Store recipe IDs as a JSON array

    if meal_time is not None:
        updates.append("meal_time = ?")
        params.append(meal_time)

    if scheduled_datetime is not None:
        updates.append("scheduled_datetime = ?")
        params.append(scheduled_datetime)

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

def get_all_meals():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select all rows from the Meal table
    meals = cursor.execute('SELECT * FROM Meal').fetchall()

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
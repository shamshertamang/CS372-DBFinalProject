-- ddl.sql

-- for normalisation documentation refer to the end of this document (ddl.sql)

PRAGMA foreign_keys = OFF;

BEGIN;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_name TEXT UNIQUE NOT NULL,
    name TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    cooking_level INTEGER CHECK ( cooking_level >= 1 and cooking_level <= 5 ),
    photo_data blob
);

-- 1-to-many for dietary preferences (one row per single preference)
CREATE TABLE IF NOT EXISTS user_dietary_preference (
    user_id     INTEGER NOT NULL
                   REFERENCES users(id) ON DELETE CASCADE,
    preference  TEXT    NOT NULL,
    PRIMARY KEY (user_id, preference)
);

-- 1-to-many for allergies (one row per single allergy)
CREATE TABLE IF NOT EXISTS user_allergy (
    user_id  INTEGER NOT NULL
                  REFERENCES users(id) ON DELETE CASCADE,
    allergy  TEXT    NOT NULL,
    PRIMARY KEY (user_id, allergy)
);
-- Done with user

--Recipes (Individual for each users)
CREATE TABLE IF NOT EXISTS recipe (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL
        REFERENCES users(id)
        On delete cascade,
    name TEXT,
    origin TEXT,
    difficulty INTEGER CHECK ( difficulty between 1 and 5 ),
    preparation_time TEXT,
    cooking_time TEXT,
    serving_size INTEGER,
    source TEXT, --_AI_or_self
    photo blob,
    UNIQUE (user_id, id, name)
);

CREATE TABLE IF NOT EXISTS recipe_step (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER NOT NULL
        REFERENCES recipe(id)
        ON DELETE CASCADE,
    step_number INTEGER NOT NULL, -- For maintaining order
    description TEXT NOT NULL,
    UNIQUE (recipe_id, step_number)
);

-- Ingredients (one name per user)
CREATE TABLE IF NOT EXISTS ingredient (
    id   INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,
    name TEXT NOT NULL,
    store TEXT,
    unit TEXT,
    seasonal_availability Text,
    UNIQUE (user_id, name)
);

-- recipe_ingredients (ingredients of each recipes)
CREATE TABLE IF NOT EXISTS recipe_ingredient (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER
        REFERENCES recipe(id)
        ON DELETE CASCADE,
    ingredient_id INTEGER
        REFERENCES ingredient (id)
        ON DELETE CASCADE,
    quantity Text,
    unit Text,
    UNIQUE (recipe_id, ingredient_id)
);

-- Meals
CREATE TABLE IF NOT EXISTS meal (
    meal_id INTEGER PRIMARY KEY,
    meal_title TEXT,
    user_id INTEGER NOT NULL
        References users(id) on delete cascade,
    meal_time TEXT CHECK (meal_time IN ('Breakfast', 'Lunch', 'Dinner', 'Snack')),
    UNIQUE (user_id, meal_title)
);

CREATE TABLE meal_recipe (
  meal_id     INTEGER NOT NULL
                REFERENCES meal(meal_id) ON DELETE CASCADE,
  recipe_id   INTEGER NOT NULL
                REFERENCES recipe(id)   ON DELETE CASCADE,
  PRIMARY KEY(meal_id, recipe_id)
);

-- if all meal_recipes are deleted, we need to delete the meal as well
CREATE TRIGGER IF NOT EXISTS trg_cleanup_orphan_meal
AFTER DELETE ON meal_recipe
FOR EACH ROW
WHEN NOT EXISTS (
  SELECT 1
    FROM meal_recipe
   WHERE meal_id = OLD.meal_id
)
BEGIN
  DELETE
    FROM meal
   WHERE meal_id = OLD.meal_id;
END;

-- Meal Plans
CREATE TABLE IF NOT EXISTS meal_plan (
    meal_plan_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    user_id INTEGER NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,
    start_date TEXT,  -- Store dates as TEXT (ISO format recommended: "YYYY-MM-DD")
    end_date TEXT,
    goals TEXT,
    UNIQUE(user_id, title)
);

--Scheduled Meals in a Meal Plan
CREATE TABLE IF NOT EXISTS meal_plan_meal (
    meal_plan_id INTEGER NOT NULL
        REFERENCES meal_plan(meal_plan_id)
        ON DELETE CASCADE,
    meal_id INTEGER NOT NULL
        REFERENCES meal(meal_id)
        ON DELETE CASCADE,
    scheduled_datetime TEXT,
    PRIMARY KEY (meal_plan_id, meal_id)
);

-- if there are no meals in a meal plan the meal plan should be deleted
CREATE TRIGGER IF NOT EXISTS trg_cleanup_orphan_mealplan
AFTER DELETE ON meal_plan_meal
FOR EACH ROW
WHEN NOT EXISTS (
  SELECT 1
    FROM meal_plan_meal
   WHERE meal_plan_id = OLD.meal_plan_id
)
BEGIN
  DELETE
    FROM meal_plan
   WHERE meal_plan_id = OLD.meal_plan_id;
END;

COMMIT;
PRAGMA foreign_keys = ON;


/*
  Database Final Project – Normalization Documentation

  1) INITIAL (Unnormalized) SCHEMA & FUNCTIONAL DEPENDENCIES

    users(
      id,
      user_name,
      name,
      email,
      password,
      cooking_level,
      photo_data,
      dietary_preferences_list,   -- e.g. CSV or array
      allergies_list              -- e.g. CSV or array
    )
      FDs:
        id → {user_name, name, email, password, cooking_level, photo_data,
               dietary_preferences_list, allergies_list}
        user_name → {user_name, name, email, password, cooking_level, photo_data,
               dietary_preferences_list, allergies_list}
        email → {user_name, name, email, password, cooking_level, photo_data,
               dietary_preferences_list, allergies_list}

    recipe(
      id,
      user_id,
      name,
      origin,
      difficulty,
      preparation_steps_list,      -- e.g. ordered text or JSON
      preparation_time,
      cooking_time,
      serving_size,
      source,
      photo,
      ingredients_list,            -- e.g. CSV of ingredient names
      store_list,                  -- parallel CSV of store names
      unit_list,                   -- parallel CSV of units
      seasonal_availability_list   -- parallel CSV of seasons
    )
      FDs:
        id → {user_id, name, origin, difficulty, preparation_steps_list,
               preparation_time, cooking_time, serving_size, source, photo,
               ingredients_list, store_list, unit_list, seasonal_availability_list}
        (user_id, name) → {user_id, name, origin, difficulty, preparation_steps_list,
               preparation_time, cooking_time, serving_size, source, photo,
               ingredients_list, store_list, unit_list, seasonal_availability_list}     -- recipe name is unique per person

    meal(
      meal_id,
      meal_title,
      user_id,
      meal_time,
      recipe_list                  -- CSV or array of recipe IDs
    )
      FDs:
        meal_id → {meal_title, user_id, meal_time, recipe_list}
        (user_id, meal_title) → {meal_title, user_id, meal_time, recipe_list}

    meal_plan(
      meal_plan_id,
      title,
      user_id,
      start_date,
      end_date,
      goals,
      scheduled_meals_list         -- CSV or JSON of (meal_id, datetime)
    )
      FDs:
        meal_plan_id → {title, user_id, start_date, end_date, goals, scheduled_meals_list}
        (user_id, title) → {title, user_id, start_date, end_date, goals, scheduled_meals_list}

  2) FIRST NORMAL FORM (1NF)
    # Removed all multi‐valued columns:
      – dietary_preferences_list → user_dietary_preference(user_id, preference)
      – allergies_list           → user_allergy(user_id, allergy)
      – preparation_steps_list   → recipe_step(recipe_id, step_number, description)
      – ingredients_list + ingredient_stores + ingredient_units, etc → recipe_ingredient(recipe_id, ingredient_id, quantity, unit)
      – recipe_list              → meal_recipe(meal_id, recipe_id)
      – scheduled_meals_list      → meal_plan_meal(meal_plan_id, meal_id, scheduled_datetime)
    # Ensured every column has a single, atomic value.

  3) SECOND NORMAL FORM (2NF)
    # All tables must either have a single‐column PK or a composite PK.
    # make sure no non‐key attribute depends on part of a composite key:
      – e.g. in meal_plan_meal, scheduled_datetime depends on (meal_plan_id, meal_id) as a whole.

  4) THIRD NORMAL FORM (3NF)
    # Ensured no non‐key attribute transitively depends on the primary key.
      – All attributes in every table depend *directly* on its PK (or full composite PK), not on another non‐key.

  5) BOYCE–CODD NORMAL FORM (BCNF)
    # Checked every non‐trivial FD X→A has X as a superkey:
      – In each table, the only determinants are either the declared PK or a declared UNIQUE key.

  REASONING SUMMARY
    • Decomposed multi‐valued and repeating groups into dedicated child tables.
    • Introduced surrogate integer IDs to keep PKs atomic and simple.
    • Used composite UNIQUE constraints where needed to preserve original uniqueness semantics.
    • Added triggers to cascade-delete orphan parents (meals & meal plans) when children are removed.
*/
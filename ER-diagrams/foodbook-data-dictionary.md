# FoodBook Data Dictionary

This data dictionary was made before I started the project. Refer to the schema in ddl.sql for updated schema.

## Entities

### 1. User
- **Entity Type:** Strong
- **Description:** Users are food enthusiasts who use the app.
- **Identifiers:** UserID (PK)
- **Attributes:**
  - *UserID* (Unique(U), PK)
  - *Username* (U)
  - *Email* (U)
  - *PasswordHash*
  - *Dietary Preferences*
  - *Cooking Level*
  - *Allergies*
  - *Subscription Status*
  - *ProfilePhotoPath*

### 2. Ingredient
- **Entity Type:** Super, Strong
- **Description:** Ingredient for recipe
- **Identifiers:** IngredientID (PK)
- **Attributes:**
  - *IngredientID* (Unique(U), PK)
  - *name* (U)
  - *store*
  - *Unit*
  - *Nutritional label* JSON data containing calories and nutrients
  - *alternative stores* JSON
  - *common substitutes* JSON
  - *Seasonal Availability*

### 3. Recipe
- **Entity Type:** Strong
- **Description:** Recipe provides steps, prep time, cook time and other valuable details of recipe. 
- **Identifiers:** RecipeID (PK)
- **Attributes:**
  - *RecipeID* (PK U)
  - *Name* (U)
  - *CollectionID* (FK)
  - *Origin*
  - *Difficulty Level*
  - *Reminder Times*
  - *Preparation Steps* (JSON support multiple steps)
  - *Preparation Time*
  - *Cooking Time*
  - *Serving*
  - *Source* : AI generated or not
  - *PhotoID* (JSON to support multiple photos) (FK) limit to 4

### 6. Recipe Photo
- **Entity Type:** Strong
- **Description:** Recipe Photo
- **Identifiers:** PhotoID (PK)
- **Attributes:**
  - *PhotoID* (PK U)
  - *RecipeID*
  - *Name* U
  - *Uploaded at*

### 7. Meal
- **Entity Type:** Strong
- **Description:** Meal within a Meal Plan, associated with recipes and time slots.
- **Identifiers:** MealID (PK)
- **Attributes:**
  - *MealID* (PK U)
  - *RecipeID* U (JSON for a list of recipeID)
  - *UserID* U
  - *MealPlanID* (FK)
  - *MealTime* (e.g., "Breakfast", "Lunch", "Dinner")
  - *ScheduledDateTime*

### 8. Meal Plan
- **Entity Type:** Strong
- **Description:** List of meals for a weekly or specified interval.
- **Identifiers:** MealPlanID (PK)
- **Attributes:**
  - *MealPlanID* (PK U)
  - *Title* U
  - *UserID* U 
  - *StartDate*
  - *EndDate*

### 9. Pantry Item
- **Entity Type:** Strong, SubType (of Ingredient)
- **Description:** Items that the user already owns, including quantity and expiration date for shelf-life tracking.
- **Identifiers:** PantryItemID (PK)
- **Attributes:**
  - *PantryItemID* (PK U)
  - *IngredientID* U
  - *Quantity*
  - *Unit*
  - *ExpirationDate*
  - *Added Date*

### 10. Shopping Items
- **Entity Type:** Strong, SubType (of Ingredient)
- **Description:** Items for the shopping list
- **Identifiers:** ShoppingItemID (PK)
- **Attributes:**
  - *ShoppingItemID* (PK U)
  - *IngredientName*
  - *Quantity*
  - *Unit*
  - *StoreName*
  - *IsPurchased* (Boolean)

### 11. Recipe Collection (based on themes and occassions)
- **Entity Type:** Strong
- **Description:** Recipe collections
- **Identifiers:** CollectionID (PK), UserID (FK)
- **Attributes:**
  - *CollectionID* (PK U)
  - *UserID (FK)
  - *Name*
  - *Description*

### 12. Recipe Ingredients
- **Entity Type:** Weak
- **Description:** Ingredient for a particular recipe
- **Identifiers:** RecipeIngredientID (PK)
- **Attributes:**
  - *RecipeIngredientID* (PK U)
  - *RecipeID*
  - *IngredientID*
  - *Quantity*
  - *Unit*

### 13. Current Recipes (V2)
- **Entity Type:** Weak
- **Description:** Aggregate all recipes for meal prep tasks
- **Identifiers:** SourceType (PK), SourceID (PK)
- **Attributes:**
  - *SourceType* (PK) (like recipe, meal, meal plan, collection)
  - *SourceID* (PK)
  - *UserID*

### 14. Meal Prep Tasks (V2)
- **Entity Type:** Weak
- **Description:** Meal prep tasks created by user or AI to optimise complex meal plans
- **Identifiers:** TaskID (PK)
- **Attributes:**
  - *TaskID* (PK U)
  - *TaskName*
  - *TaskDescription*
  - *TaskType* (eg. chopping marinating)
  - *time* 
  - *Assigned to*
  - *isCompleted*
  - *CurrentRecipes* (FK)

## Relationships

### 1. Has(User - Ingredient)
- **Description:** User has 0, 1 or many ingredients
- **Cardinality:** One-Many

### 2. Creates(User-Recipe)
- **Description:** A user can create 0, 1 or many recipes
- **Cardinality:** One-Many

### 3. Belongs to (Recipe - Recipe Collection)
- **Description:** A recipe belongs to 0, 1 or many collections and vice versa
- **Cardinality:** Many-Many

### 4. Contains (Recipe - Ingredients)
- **Description:** A recipe uses 1 or Many ingredients. An ingredient can appear in 0, 1 or many recipes.
- **Cardinality:** Many-Many

### 5. Has (Recipe - Photos)
- **Description:** A recipe can have upto 4 photos. Each photo belongs to a recipe.
- **Cardinality:** One-Many

### 6. Uploads (User - Photos)
- **Description:** A user can upload 1 profile photo and 0, 1 or many recipe photos.
- **Cardinality:** One-One for profile and One-Many for Recipe Phots

### 7. Plans (User - Meal Plans)
- **Description:** A user plans 0, 1 or many meal plans.
- **Cardinality:** One-Many

### 8. Serves (Meal - Recipe)
- **Description:** A meal can consist of 1 or Many recipes. A recipe can be used for 0, 1 or many meals
- **Cardinality:** Many-Many

### 9. IncludesMeals (MealPlan–Meal)
- **Description:** A meal plan includes one or many meals; each meal belongs to can belong to one or multiple meal plans.
- **Cardinality:** Many‑Many

### 10. Owns (User–PantryItem)
- **Description:** A user can have zero, one, or many pantry items.
- **Cardinality:** One‑Many

### 11. Tracks (PantryItem–Ingredient)
- **Description:** Each pantry item refers to exactly one ingredient; an ingredient can be tracked in zero, one, or many pantry items.
- **Cardinality:** Many‑One

### 12. Lists (User–ShoppingItem)
- **Description:** A user can have zero, one, or many shopping‑list items.
- **Cardinality:** One‑Many

### 13. References (ShoppingItem–Ingredient)
- **Description:** Each shopping‑list item names one ingredient; an ingredient can appear on zero, one, or many shopping lists.
- **Cardinality:** Many‑One

### 14. Aggregates (CurrentRecipes–Recipe/Meal/MealPlan/RecipeCollection)
- **Description:** The CurrentRecipes table brings together any “source” (recipe, meal, plan, or collection) for V2 tasks.
- **Cardinality:** Many-Many

### 15. Assigns (CurrentRecipes–MealPrepTask) for version 2
- **Note:** Requires more brainstorming as of now
- **Description:** Each “current recipe” (i.e. any source in V2) can have zero, one, or many meal‑prep tasks; each task belongs to exactly one current‑recipes record.
- **Cardinality:** One‑Many

## Business Rules
1. User can create and delete an account.
2. Deleting a user cascade deletes all the recipes that the user has.
3. Every recipe, ingredient, meal, meal plan belongs to a valid User.
4. Pantry Item, Shopping Items contain ingredients.
5. If Pantry Item, Shopping Items are not contained in ingredients, new ingredients are created.
4. Each recipe can have only upto 4 photos.
5. Recipe Ingredients contains ingredients for recipe.
6. Recipe collection is a collection of recipes.
7. User can upload one photo only.
# views.py
from collections import deque

from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from flask_login import login_required, current_user, logout_user
from unicodedata import category
from .database import (
    get_user_by_id, update_user_profile, delete_user_by_id, get_all_recipes, create_recipe,
    get_db_connection, get_user_by_email, create_ingredient, create_recipe_ingredient, get_recipe,
    get_recipe_ingredients, update_recipe, delete_recipe_ingredient, get_ingredients, get_recipe_by_name, create_meal,
    get_all_meals, get_meal, update_meal, delete_meal as delete_meal_db
)
import json, re, base64


views = Blueprint('views', __name__)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# ----------- Home Page Routing -----------
@views.route('/', methods=['GET'])
@login_required
def home():
    # get all recipes
    rows = get_all_recipes()
    recipes = []
    for row in rows:
        rec = dict(row)
        rec['photos'] = json.loads(rec.get('photos_json') or '[]')
        recipes.append(rec)
    # get all meals
    rows = get_all_meals()
    meals = []
    for row in rows:
        meal = dict(row)
        meal['photos'] = []

        recipe_ids = json.loads(meal['recipe_ids'])
        first_recipe_photo = None
        for recipe_id in recipe_ids:
            recipe = get_recipe(recipe_id)
            if recipe and recipe['photos_json']:
                photos = json.loads(recipe['photos_json'])
                if photos:
                    first_recipe_photo = photos[0]
                    break

        meal['photos'] = first_recipe_photo
        meals.append(meal)
    return render_template("home.html", user=current_user, recipes=recipes, meals= meals)


@views.route('/add-recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        origin = request.form.get('origin', '').strip()
        difficulty_raw = request.form.get('difficulty_level', '')
        prep_steps_raw = request.form.get('preparation_steps', '')
        prep_time = request.form.get('preparation_time', '').strip()
        cook_time = request.form.get('cooking_time', '').strip()
        serving_raw = request.form.get('serving', '')
        source = request.form.get('source', '').strip()
        ingredients_raw = request.form.get('ingredients', '')

        index = get_recipe_by_name(name)
        if index:
            flash(message='Recipe with this name already exists. You have been directed to edit the recipe.', category='error')
            return redirect(url_for('views.edit_recipe', recipe_id=index))
        # Basic validation
        if not name or not prep_steps_raw or not ingredients_raw or not serving_raw:
            flash('Please fill out required fields: Name, Steps, Ingredients, Serving Size.', 'error')
            return redirect(url_for('views.add_recipe'))

        # Parse and default values
        try:
            difficulty = int(difficulty_raw)
        except ValueError:
            difficulty = 1
        try:
            prep_time = str(int(prep_time))
        except ValueError:
            prep_time = '0'
        try:
            cook_time = str(int(cook_time))
        except ValueError:
            cook_time = '0'
        try:
            serving_size = int(serving_raw)
        except ValueError:
            serving_size = 1

        preparation_steps = [s.strip() for s in prep_steps_raw.split(',') if s.strip()]
        ingredients = [i.strip() for i in ingredients_raw.split(',') if i.strip()]

        # Insert recipe
        try:
            recipe_id = create_recipe(
                user_id=current_user.id,
                name=name,
                origin=origin,
                difficulty=difficulty,
                preparation_steps=preparation_steps,
                preparation_time=prep_time,
                cooking_time=cook_time,
                serving_size=serving_size,
                source=source or 'Unknown',
                photos=[]
            )

            for ingredient_name in ingredients:
                # Ensure ingredient exists for this user
                row = get_ingredients(user_id=current_user.id, name_query=ingredient_name)
                if row:
                    ingredient_id = row['id']
                else:
                    ingredient_id = create_ingredient(user_id=current_user.id, name=ingredient_name)

                # Link recipe <-> ingredient
                create_recipe_ingredient(recipe_id, ingredient_id)

            flash('Recipe created successfully!', 'success')
            return redirect(url_for('views.home'))
        except Exception as e:
            flash(f'Error creating recipe: {e}', 'error')
            return redirect(url_for('views.add_recipe'))
    return render_template('add_recipe.html', user=current_user)


@views.route('/delete-recipe/<int:recipe_id>', methods=['POST', 'GET'])
@login_required
def delete_recipe(recipe_id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipe WHERE id = ?', (recipe_id,)).fetchone()

    if recipe is None:
        conn.close()
        flash('Recipe not found.', category='error')
        return redirect(url_for('views.home'))

    conn.execute('DELETE FROM recipe WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()

    flash('Recipe deleted successfully!', category='success')
    return redirect(url_for('views.home'))


@views.route('/edit-recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    # get recipe and ingredient from queries
    recipe = get_recipe(recipe_id)

    ingredients = get_recipe_ingredients(recipe_id)

    if recipe is None:
        flash('Recipe not found.', category='error')
        return redirect(url_for('views.home'))

    # post request handling
    if request.method == 'POST':
        name = request.form.get('name')
        origin = request.form.get('origin')
        try:
            difficulty = int(request.form.get('difficulty_level') or 1)
        except ValueError:
             difficulty = 1
        preparation_steps_raw = request.form.get('preparation_steps')
        ingredients_raw = request.form.get('ingredients')
        preparation_time = request.form.get('preparation_time')
        cooking_time = request.form.get('cooking_time')
        try:
            serving_size = int(request.form.get('serving') or 1)
        except ValueError:
            serving_size = 1
        source = request.form.get('source')

        photo_files = request.files.getlist('photos')
        existing = json.loads(recipe['photos_json'] or '[]')
        photo_blobs = deque(existing, maxlen=4)

        for f in photo_files[:4]:
            if f and f.filename:
                data = f.read()
                photo_blobs.append(base64.b64encode(data).decode('utf-8'))

        if not name or not preparation_steps_raw or not ingredients_raw:
            flash('Please fill out required fields.', category='error')
        else:
            # update recipe table
            preparation_steps = [step.strip() for step in preparation_steps_raw.split(',') if step.strip()]
            update_recipe(name=name, origin=origin, difficulty=difficulty,
                          preparation_steps=preparation_steps, preparation_time=preparation_time,
                          cooking_time=cooking_time, serving_size=serving_size, source=source,
                          photos=photo_blobs, recipe_id=recipe_id)

            # delete existing recipe_ingredients
            delete_recipe_ingredient(recipe_id)

            # add the new ingredients
            ingredients = [ingredient.strip() for ingredient in ingredients_raw.split(',') if ingredient.strip()]
            for ingredient_name in ingredients:
                existing_ingredient = get_ingredients(user_id=current_user.id, name_query=ingredient_name)

                if existing_ingredient:
                    ingredient_id = existing_ingredient['id']
                else:
                    ingredient_id = create_ingredient(user_id=current_user.id, name=ingredient_name)

                create_recipe_ingredient(recipe_id=recipe_id, ingredient_id=ingredient_id)

            flash('Recipe updated successfully!', category='success')
            return redirect(url_for('views.view_recipe', recipe_id=recipe_id))

    preparation_steps = json.loads(recipe['preparation_steps']) if recipe['preparation_steps'] else []

    return render_template('edit_recipe.html', user=current_user, recipe=recipe,
                           preparation_steps=preparation_steps, ingredients=ingredients)


@views.route('/recipe/<int:recipe_id>')
@login_required
def view_recipe(recipe_id):
    recipe_ = get_recipe(recipe_id)
    if recipe_ is None:
        flash('Recipe not found.', category='error')
        return redirect(url_for('views.home'))

    ingredients = get_recipe_ingredients(recipe_id)
    if ingredients is None:
        flash('Ingredients not found. You need to add ingredients to the recipe', category='error')
        return redirect(url_for('views.edit_recipe', recipe_id=recipe_id))

    preparation_steps = json.loads(recipe_['preparation_steps']) if recipe_['preparation_steps'] else []

    recipe = dict(recipe_)
    recipe['photos'] = json.loads(recipe.get('photos_json') or '[]')

    return render_template('view_recipe.html', user=current_user, recipe=recipe,
                           preparation_steps=preparation_steps, ingredients=ingredients)

# ----------- Meal Related Routing -----------
@views.route('/add-meal', methods=['GET', 'POST'])
@login_required
def add_meal():
    rows = get_all_recipes()
    recipes = [dict(row) for row in rows]

    if not recipes:
        flash('No recipes found. Please add recipes to add to meal.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        meal_title = request.form.get('meal_title').strip()
        meal_time = request.form.get('meal_time').strip()  # E.g., "Breakfast", "Lunch", "Dinner"
        scheduled_datetime = request.form.get('scheduled_datetime').strip()  # "YYYY-MM-DD HH:MM:SS"
        recipe_ids_raw = request.form.getlist('recipe_ids')  # Comma-separated list of recipe IDs
        recipe_ids = [int(r.strip()) for r in recipe_ids_raw if r.strip()]

        if not meal_time or not scheduled_datetime or not recipe_ids:
            flash('Please fill out all fields', category='error')
            return redirect(url_for('views.add_meal'))

        try:
            meal_id = create_meal(
                user_id=current_user.id,
                recipe_ids=recipe_ids,
                meal_title=meal_title,
                meal_time=meal_time,
                scheduled_datetime=scheduled_datetime
            )
            flash('Meal created successfully!', category='success')
            return redirect(url_for('views.view_meal', meal_id=meal_id))
        except Exception as e:
            flash(f'Error creating meal: {e}', category='error')
            return redirect(url_for('views.add_meal'))

    rows = get_all_recipes()
    recipes = []
    for row in rows:
        recipes.append(dict(row))
    return render_template('add_meal.html', user=current_user, recipes=recipes)

@views.route('/meal/<int:meal_id>')
@login_required
def view_meal(meal_id):
    meal = get_meal(meal_id)
    if meal is None:
        flash('Meal not found.', category='error')
        return redirect(url_for('views.home'))

    # Retrieve recipes associated with the meal
    recipe_ids = json.loads(meal['recipe_ids'])  # Deserialize JSON array of recipe IDs
    meal_recipes = []
    unique_ingredients = set()

    for recipe_id in recipe_ids:
        recipe_raw = get_recipe(recipe_id)
        if not recipe_raw:
            continue
        rec = dict(recipe_raw)
        ingr_rows = get_recipe_ingredients(recipe_id)
        ingredients = [row['name'] for row in ingr_rows]
        rec['ingredients'] = list(dict.fromkeys(ingredients))
        unique_ingredients.update(rec['ingredients'])
        rec['preparation_steps'] = json.loads(rec.get('preparation_steps') or '[]')
        meal_recipes.append(rec)



    return render_template('view_meal.html', user=current_user, meal=meal,
                           meal_recipes=meal_recipes, unique_ingredients=unique_ingredients)

@views.route('/edit-meal/<int:meal_id>', methods=['GET', 'POST'])
@login_required
def edit_meal(meal_id):
    meal = get_meal(meal_id)
    if not meal or meal['user_id'] != current_user.id:
        flash('Meal not found.', 'error')
        return redirect(url_for('views.home'))

    # on POST: pull form fields, call update_meal(...)
    if request.method == 'POST':
        title = request.form['meal_title']
        time  = request.form['meal_time']
        sched = request.form['scheduled_datetime']
        ids   = [int(r) for r in request.form.getlist('recipe_ids')]
        update_meal(meal_id, recipe_ids=ids, meal_time=time, scheduled_datetime=sched)
        flash('Meal updated!', 'success')
        return redirect(url_for('views.view_meal', meal_id=meal_id))

    # on GET: pre-load all recipes, mark the ones in this meal
    all_recipes = [dict(r) for r in get_all_recipes()]
    selected = set(json.loads(meal['recipe_ids']))
    return render_template('edit_meal.html',
                           user=current_user,
                           meal=meal,
                           recipes=all_recipes,
                           selected_recipe_ids=selected)

@views.route('/delete-meal/<int:meal_id>', methods=['POST'])
@login_required
def delete_meal(meal_id):
    # note: this is shadowing the imported name, but that's OK
    try:
        delete_meal_db(meal_id)           # calls the DB function
        flash('Meal deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting meal: {e}', 'error')
    return redirect(url_for('views.home')+'#meals')

# ----------- Profile Page Routing -----------
@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    if request.method == 'POST':
        photo_data = None
        file = request.files.get('profile_picture')
        if file and file.filename != '':
            photo_data = file.read()

        new_user_name = request.form.get('user_name', '').strip()
        new_email = request.form.get('email', '').strip()

        raw_prefs = request.form.get('dietary_preferences')
        new_dietary_preferences = [p.strip() for p in raw_prefs.split(',') if p.strip()] if raw_prefs else []

        cooking_level_raw = request.form.get('cooking_level')
        try:
            new_cooking_level = int(cooking_level_raw)
            if new_cooking_level not in range(1, 6):
                raise ValueError
        except (ValueError, TypeError):
            flash('Cooking level must be an integer between 1 and 5.', category='error')
            return redirect(url_for('views.profile_page'))

        # new_allergies = request.form.get('allergies')
        raw_allergies = request.form.get('allergies', '')
        new_allergies = [a.strip() for a in raw_allergies.split(',') if a.strip()] if raw_allergies else []

        new_subscription_status = request.form.get('subscription_status', '').strip()

        if not new_user_name:
            new_user_name = current_user.user_name

        if not new_email:
            new_email = current_user.email

        if not new_dietary_preferences:
            new_dietary_preferences = current_user.dietary_preferences

        if not new_allergies:
            new_allergies = current_user.allergies

        if not new_subscription_status:
            new_subscription_status = current_user.subscription_status

        if not is_valid_email(new_email):
            flash('Invalid email format.', category='error')
            return redirect(url_for('views.profile_page'))

        if new_email != current_user.email:
            email_owner = get_user_by_email(new_email)
            if email_owner and email_owner.id != current_user.id:
                flash('That email is already in use by another account.', category='error')
                return redirect(url_for('views.profile_page'))

        if not new_cooking_level in range(1, 6):
            flash('Cooking level must be between 1 and 5.', category='error')
            return redirect(url_for('views.profile_page'))

        try:
            update_user_profile(
                user_id=current_user.id,
                user_name=new_user_name,
                email=new_email,
                dietary_preferences=new_dietary_preferences,
                cooking_level=new_cooking_level,
                allergies=new_allergies,
                subscription_status=new_subscription_status,
                photo_data=photo_data
            )
            flash('Profile page updated!', category='success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', category='error')

        return redirect(url_for('views.profile_page'))

    updated_user = get_user_by_id(current_user.id)
    profile_image_data = None
    if updated_user.profile_image:  # assuming this is a BLOB (bytes)
        profile_image_data = base64.b64encode(updated_user.profile_image).decode('utf-8')

    return render_template("profile.html", user=updated_user,
                           profile_image_data = profile_image_data)

@views.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    try:
        delete_user_by_id(current_user.id)
        # need to delete ingredients
        # need to delete recipe ingredients
        # need to delete recipes
        # need to delete recipe ids
        # need to delete meals
        # need to delete meal plan
        # need to delete mealplanmeal
        logout_user()
        flash("Your account has been deleted. We're sorry to see you go 💔", category='success')

        return redirect(url_for('auth.login'))

    except Exception as e:
        flash(f"Something went wrong: {str(e)}", category='error')
        return redirect(url_for('views.profile_page'))
# views.py
from collections import deque

from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user, logout_user
from .database import (
    get_user_by_id, update_user_profile, delete_user_by_id, get_all_recipes, create_recipe,
    get_db_connection, get_user_by_email, create_ingredient, create_recipe_ingredient, get_recipe,
    get_recipe_ingredients, update_recipe, delete_recipe_ingredient, get_ingredients, get_recipe_by_name, create_meal,
    get_all_meals, get_meal, update_meal, delete_meal as delete_meal_db, get_meal_by_name, create_meal_plan,
    add_meal_to_plan, get_meal_plan, get_meal_plan_meals_and_schedules,
    get_meal_plan_by_user_and_title, delete_meal_plan_and_meal_plan_meals_by_id, get_all_meal_plans, update_meal_plan,
    delete_meal_plan_meal, get_recipe_steps, get_recipe_in_meal, get_recipe_ids_for_meal, delete_recipes_from_meal,
    add_recipe_to_meal, delete_recipe_from_meal_recipe, update_meal_plan_meal_schedule, create_meal_plan_with_schedule
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
    rows = get_all_recipes(current_user.id)
    recipes = []
    for row in rows:
        rec = dict(row)
        blob = rec.pop('photo')
        rec['photo'] = base64.b64decode(blob).decode('utf-8') if blob else None
        recipes.append(rec)

    # get all meals
    # get all meals (no photos)
    rows = get_all_meals(current_user.id)
    meals = [{
            'meal_id': r['meal_id'],
            'meal_title': r['meal_title'],
            'meal_time': r['meal_time']
    } for r in rows]

    meal_plans = get_all_meal_plans(current_user.id)
    return render_template("home.html", user=current_user, recipes=recipes, meals= meals,
                           meal_plans=meal_plans)


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

        file = request.files.get('photo')
        photo_data = file.read() if file and file.filename else None

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
                photo_data=photo_data
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

        # single-photo upload
        file = request.files.get('photo')
        photo_data = None

        if file and file.filename:
            photo_data = file.read()

        if not name or not preparation_steps_raw or not ingredients_raw:
            flash('Please fill out required fields.', category='error')
        else:
            # update recipe table
            preparation_steps = [step.strip() for step in preparation_steps_raw.split(',') if step.strip()]
            update_recipe(name=name, origin=origin, difficulty=difficulty,
                          preparation_steps=preparation_steps, preparation_time=preparation_time,
                          cooking_time=cooking_time, serving_size=serving_size, source=source,
                          photo_data=photo_data, recipe_id=recipe_id)

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

    preparation_steps = get_recipe_steps(recipe_id)

    return render_template('edit_recipe.html', user=current_user, recipe=recipe,
                           preparation_steps=preparation_steps, ingredients=ingredients)


@views.route('/recipe/<int:recipe_id>')
@login_required
def view_recipe(recipe_id):
    recipe_row = get_recipe(recipe_id)
    if not recipe_row:
        flash('Recipe not found.', category='error')
        return redirect(url_for('views.home'))

    recipe = dict(recipe_row)
    blob = recipe.pop('photo')
    recipe['photo'] = base64.b64encode(blob).decode('utf-8') if blob else None

    ingredients = get_recipe_ingredients(recipe_id)

    ingredients = [r['name'] for r in ingredients]

    preparation_steps = get_recipe_steps(recipe_id)

    return render_template('view_recipe.html', user=current_user, recipe=recipe,
                           preparation_steps=preparation_steps, ingredients=ingredients)

# ----------- Meal Related Routing -----------
@views.route('/add-meal', methods=['GET', 'POST'])
@login_required
def add_meal():
    rows = get_all_recipes(current_user.id)
    recipes = [dict(row) for row in rows]

    if not recipes:
        flash('No recipes found. Please add recipes to add to meal.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        meal_title = request.form.get('meal_title', '').strip()
        meal_time = request.form.get('meal_time').strip()  # E.g., "Breakfast", "Lunch", "Dinner"
        # scheduled_datetime = request.form.get('scheduled_datetime').strip()  # "YYYY-MM-DD HH:MM:SS"
        recipe_ids_raw = request.form.getlist('recipe_ids')  # Comma-separated list of recipe IDs
        recipe_ids = [int(r.strip()) for r in recipe_ids_raw if r.strip()]

        # if not meal_time or not scheduled_datetime or not recipe_ids:
        if get_meal_by_name(user_id = current_user.id, meal_title = meal_title):
            flash('Meal already exists by this name.', category='error')
            return redirect(url_for('views.add_meal'))

        if not meal_time or not recipe_ids:
            flash('Please fill out all fields', category='error')
            return redirect(url_for('views.add_meal'))

        try:
            meal_id = create_meal(
                user_id=current_user.id,
                recipe_ids=recipe_ids,
                meal_title=meal_title,
                meal_time=meal_time,
                # scheduled_datetime=scheduled_datetime
            )
            flash('Meal created successfully!', category='success')
            return redirect(url_for('views.view_meal', meal_id=meal_id))
        except Exception as e:
            flash(f'Error creating meal: {e}', category='error')
            return redirect(url_for('views.add_meal'))

    return render_template('add_meal.html', user=current_user, recipes=recipes)

@views.route('/meal/<int:meal_id>')
@login_required
def view_meal(meal_id):
    meal = get_meal(meal_id)

    if meal is None or meal['user_id'] != current_user.id:
        flash('Meal not found.', category='error')
        return redirect(url_for('views.home'))

    # Retrieve recipes associated with the meal
    recipes = get_recipe_in_meal(meal_id)
    meal_recipes = []
    unique_ingredients = set()

    for recipe in recipes:
        rec = dict(recipe)
        recipe_id = rec['id']

        # fetch ordered preparation steps
        rec['preparation_steps'] = get_recipe_steps(recipe_id)

        # fetch and attach ingredient list for this recipe
        ingr_rows = get_recipe_ingredients(recipe_id)
        ingredients = [row['name'] for row in ingr_rows]
        rec['ingredients'] = ingredients

        unique_ingredients.update(rec['ingredients'])

        meal_recipes.append(rec)

    unique_ingredients = list(unique_ingredients)

    return render_template('view_meal.html', user=current_user, meal=meal,
                           meal_recipes=meal_recipes, unique_ingredients=unique_ingredients)

@views.route('/edit-meal/<int:meal_id>', methods=['GET', 'POST'])
@login_required
def edit_meal(meal_id):
    meal = get_meal(meal_id)
    if not meal or meal['user_id'] != current_user.id:
        flash('Meal not found.', 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        title = request.form['meal_title'].strip()
        time  = request.form['meal_time'].strip()
        new_ids = {int(r) for r in request.form.getlist('recipe_ids')}

        if not new_ids:
            flash('Select at least one recipe', category='error')
            return redirect(url_for('views.edit_meal', meal_id= meal_id))

        existing_meal = get_meal_by_name(user_id=current_user.id, meal_title=title)
        if existing_meal and existing_meal != meal_id:
            flash('Meal already exists by this name.', category='error')
            return redirect(url_for('views.edit_meal', meal_id= meal_id))
        update_meal(meal_id, meal_title=title, meal_time=time)

        old_ids = set(get_recipe_ids_for_meal(meal_id))
        for recipe_id in (old_ids-new_ids):
            delete_recipe_from_meal_recipe(meal_id, recipe_id)

        for recipe_id in (new_ids-old_ids):
            add_recipe_to_meal(meal_id, recipe_id)

        flash('Meal updated!', 'success')
        return redirect(url_for('views.view_meal', meal_id=meal_id))

    # on GET: pre-load all recipes, mark the ones in this meal
    all_recipes = [dict(r) for r in get_all_recipes(current_user.id)]
    selected = set(get_recipe_ids_for_meal(meal_id))
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

# ----------- Meal Plan related Routing -----------
@views.route('/add-meal-plan', methods=['GET', 'POST'])
@login_required
def add_meal_plan():
    if request.method == 'POST':
        title      = request.form.get('plan_title', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date   = request.form.get('end_date', '').strip()
        goals      = request.form.get('goals', '').strip()

        meal_ids = [int(m) for m in request.form.getlist('meal_ids')]

        if not title or not start_date or not end_date:
            flash('Please provide a title, start date and end date.', 'error')
            return redirect(url_for('views.add_meal_plan'))
        if start_date > end_date:
            flash('Start date must be on or before end date.', 'error')
            return redirect(url_for('views.add_meal_plan'))
        if not meal_ids:
            flash('Select at least one meal for your plan.', 'error')
            return redirect(url_for('views.add_meal_plan'))

        if get_meal_plan_by_user_and_title(current_user.id, title):
            flash('Meal plan already exists with that title.', 'error')
            return redirect(url_for('views.add_meal_plan'))

        valid_ids = {m['meal_id'] for m in get_all_meals(current_user.id)}
        if set(meal_ids)-valid_ids:
            flash("Invalid meal selected.", 'error')
            return redirect(url_for('views.add_meal_plan'))

        schedule_map = {}
        for m in meal_ids:
            dt = request.form.get(f'schedule_{m}', '').strip()
            if not dt:
                flash('Each selected meal must have a date/time.', 'error')
                return redirect(url_for('views.add_meal_plan'))
            schedule_map[m] = dt


        try:
            plan_id = create_meal_plan_with_schedule(
                user_id=current_user.id,
                title=title,
                start_date=start_date,
                end_date=end_date,
                goals=goals,
                schedule_map=schedule_map
            )

            flash('Meal plan created successfully!', 'success')
            return redirect(url_for('views.view_meal_plan', meal_plan_id=plan_id))

        except Exception as e:
            flash(f'Error creating meal plan: {e}', 'error')
            return redirect(url_for('views.add_meal_plan'))

    # GET → load form, passing only this user’s meals
    all_meals = get_all_meals(current_user.id)
    if not all_meals:
        flash('No meals found. Please add meals first', 'info')
    meals = [dict(m) for m in all_meals]
    return render_template('add_meal_plan.html', user=current_user, meals=meals)


@views.route('/view-meal-plan/<int:meal_plan_id>', methods=['GET'])
@login_required
def view_meal_plan(meal_plan_id):
    plan = get_meal_plan(meal_plan_id, current_user.id)

    # Not found or not owned by this user?
    if not plan or plan['user_id'] != current_user.id:
        flash('Meal plan not found or access denied.', 'error')
        return redirect(url_for('views.home'))

    rows = get_meal_plan_meals_and_schedules(meal_plan_id)
    scheduled_meals = [dict(r) for r in rows]

    return render_template(
        'view_meal_plan.html',
        user=current_user,
        plan=plan,
        scheduled_meals=scheduled_meals
    )

@views.route('/edit-meal-plan/<int:meal_plan_id>', methods=['GET', 'POST'])
@login_required
def edit_meal_plan(meal_plan_id):
    plan = get_meal_plan(meal_plan_id, user_id=current_user.id)
    if not plan:
        flash('Meal plan not found or access denied.', 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # pull in form values
        title = request.form.get('plan_title', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        goals = request.form.get('goals', '').strip()
        meal_ids = [int(m) for m in request.form.getlist('meal_ids')]

        # basic validation
        if not title or not start_date or not end_date:
            flash('Please provide title, start date and end date.', 'error')
            return redirect(url_for('views.edit_meal_plan', meal_plan_id=meal_plan_id))
        if start_date > end_date:
            flash('Start date must be on or before end date.', 'error')
            return redirect(url_for('views.edit_meal_plan', meal_plan_id=meal_plan_id))
        if not meal_ids:
            flash('Select at least one meal for your plan.', 'error')
            return redirect(url_for('views.edit_meal_plan', meal_plan_id=meal_plan_id))

        existing = get_meal_plan_by_user_and_title(current_user.id, title)
        if existing and existing != meal_plan_id:
            flash("You already have a plan by that title.", "error")
            return redirect(url_for('views.edit_meal_plan', meal_plan_id=meal_plan_id))

        # collect each meal's datetime
        schedule_map = {}
        for m in meal_ids:
            dt = request.form.get(f'schedule_{m}', '').strip()
            if not dt:
                flash('Each selected meal must have a date/time.', 'error')
                return redirect(url_for('views.edit_meal_plan', meal_plan_id=meal_plan_id))
            schedule_map[m] = dt

        existing_rows = get_meal_plan_meals_and_schedules(meal_plan_id)
        old_map = {r['meal_id']: r['scheduled_datetime'] for r in existing_rows}
        new_map = schedule_map

        # update the MealPlan record
        update_meal_plan(title, start_date, end_date, goals, meal_plan_id)

        old_ids = set(old_map)
        new_ids = set(new_map)

        for removed in old_ids-new_ids:
            delete_meal_plan_meal(meal_plan_id, removed)
        for added in new_ids-old_ids:
            add_meal_to_plan(meal_plan_id, added, new_map[added])

        for kept in new_ids & old_ids:
            if new_map[kept] != old_map[kept]:
                update_meal_plan_meal_schedule(meal_plan_id, kept, new_map[kept])

        flash('Meal plan updated successfully!', 'success')
        return redirect(url_for('views.view_meal_plan', meal_plan_id=meal_plan_id))

    # GET → pre-load meals & their existing schedule entries
    all_meals = [dict(m) for m in get_all_meals(current_user.id)]
    scheduled_meals = [dict(r) for r in get_meal_plan_meals_and_schedules(meal_plan_id)]
    return render_template(
        'edit_meal_plan.html',
        user=current_user,
        plan=plan,
        meals=all_meals,
        scheduled_meals=scheduled_meals
    )

@views.route('/delete-meal-plan/<int:meal_plan_id>', methods=['POST'])
@login_required
def delete_meal_plan(meal_plan_id):

    plan = get_meal_plan(meal_plan_id, current_user.id)
    if not plan or plan['user_id'] != current_user.id:
        flash('Meal plan not found or access denied.', 'error')
        return redirect(url_for('views.home'))

    try:
        delete_meal_plan_and_meal_plan_meals_by_id(meal_plan_id)
        flash('Meal plan deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting meal plan: {e}', 'error')

    return redirect(url_for('views.home')+'#meal-plans')

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

        if not new_user_name:
            new_user_name = current_user.user_name

        if not new_email:
            new_email = current_user.email

        if not new_dietary_preferences:
            new_dietary_preferences = current_user.dietary_preferences

        if not new_allergies:
            new_allergies = current_user.allergies


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
        logout_user()
        flash("Your account has been deleted. We're sorry to see you go 💔", category='success')

        return redirect(url_for('auth.login'))

    except Exception as e:
        flash(f"Something went wrong: {str(e)}", category='error')
        return redirect(url_for('views.profile_page'))
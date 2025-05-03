-- get user, dietary_preferences by email
SELECT u.id, u.user_name, u.name, u.email, u.password, u.cooking_level, u.photo_data,
    COALESCE(
        (SELECT json_group_array(preference)
        FROM user_dietary_preference
        WHERE user_id = u.id), '[]'
    ) AS dietary_preferences,
    COALESCE(
        (SELECT json_group_array(allergy)
        FROM user_allergy
        WHERE user_id = u.id), '[]'
    ) AS allergies
FROM users AS u
WHERE u.email = ?
;

-- get user, dietary_preferences by user_name
SELECT u.id, u.user_name, u.name, u.email, u.password, u.cooking_level, u.photo_data,
    COALESCE(
        (SELECT json_group_array(preference)
        FROM user_dietary_preference
        WHERE user_id = u.id), '[]'
    ) AS dietary_preferences,
    COALESCE(
        (SELECT json_group_array(allergy)
        FROM user_allergy
        WHERE user_id = u.id), '[]'
    ) AS allergies
FROM users AS u
WHERE u.user_name = ?
;

INSERT INTO users (email, user_name, password, cooking_level, photo_data)
VALUES (?, ?, ?, ?, ?);

INSERT INTO user_dietary_preference (user_id, preference)
VALUES (?, ?);

INSERT INTO user_allergy (user_id, allergy)
VALUES (?,?);

Update users
set user_name = ?, email = ?, cooking_level = ?, photo_data = ?
where id = ?;

DELETE FROM user_dietary_preference WHERE user_id = ?;

INSERT INTO user_dietary_preference (user_id, preference)
VALUES (?, ?);

DELETE FROM user_allergy WHERE user_id = ?;

INSERT INTO user_allergy (user_id, allergy)
VALUES (?, ?);

DELETE FROM users WHERE id = ?;

INSERT INTO Ingredient (
    user_id, name, store, unit, seasonal_availability
) VALUES (?, ?, ?, ?, ?);


SELECT *
FROM ingredient
WHERE user_id = ? AND LOWER(name) LIKE LOWER(?);

INSERT INTO recipe_ingredient (
    recipe_id, ingredient_id, quantity, unit
) VALUES (?, ?, ?, ?);


SELECT ingredient.name
FROM ingredient
JOIN recipe_ingredient ON ingredient.id = recipe_ingredient.ingredient_id
WHERE recipe_ingredient.recipe_id = ?;

DELETE FROM recipe_ingredient WHERE recipe_id = ?;

INSERT INTO recipe (
    user_id, name, origin, difficulty,
    preparation_time, cooking_time,
    serving_size, source, photo
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);


SELECT r.id, r.name, r.origin, r.photo
FROM recipe AS r
WHERE r.user_id = ?
ORDER BY r.id;


SELECT * FROM recipe
WHERE id = ? and user_id = ?;

SELECT id FROM recipe
WHERE name = ? and user_id = ?;

DELETE FROM recipe WHERE id = ?;


UPDATE recipe
SET name = ?, origin = ?, difficulty = ?, preparation_time = ?, cooking_time = ?,
    serving_size = ?, source = ?, photo = ?
WHERE id = ?;

UPDATE recipe
    SET name = ?, origin = ?, difficulty = ?, preparation_time = ?, cooking_time = ?,
        serving_size = ?, source = ?
    WHERE id = ?;

INSERT INTO recipe_step (recipe_id, step_number, description)
VALUES (?, ?, ?);

Delete FROM recipe_step where recipe_id = ?;


SELECT description
  FROM recipe_step
 WHERE recipe_id = ?
 ORDER BY step_number;


Select r.id, r.name, r.origin, r.photo, r.difficulty, r.cooking_time, r.serving_size, r.source
FROM recipe AS r
Join meal_recipe AS mr ON r.id = mr.recipe_id
WHERE mr.meal_id = ?;



SELECT recipe_id FROM meal_recipe WHERE meal_id = ?;


DELETE FROM meal_recipe WHERE meal_id = ?;


DELETE FROM meal_recipe WHERE meal_id = ? and recipe_id = ?;


INSERT INTO meal_recipe (meal_id, recipe_id) VALUES (?, ?);

INSERT INTO Meal (user_id, meal_title, meal_time)
VALUES (?, ?, ?);


DELETE FROM Meal WHERE meal_id = ?;


UPDATE Meal
SET {set_clause}
WHERE meal_id = ?;


SELECT * FROM Meal WHERE meal_id = ?;


SELECT * FROM meal where user_id = ?;


SELECT * FROM Meal
where meal_id = ?;


SELECT meal_id FROM Meal
where user_id = ? and meal_title = ?;


INSERT INTO meal_plan (user_id, title, start_date, end_date, goals)
VALUES (?, ?, ?, ?, ?);


INSERT INTO meal_plan_meal(meal_plan_id, meal_id, scheduled_datetime)
VALUES (?,?, ?);


INSERT INTO meal_plan_meal
(meal_plan_id, meal_id, scheduled_datetime)
VALUES (?, ?, ?);


SELECT * FROM meal_plan WHERE meal_plan_id = ? and user_id = ?;


SELECT m.meal_id, m.meal_title, ppm.scheduled_datetime
FROM meal_plan_meal AS ppm
JOIN meal AS m ON ppm.meal_id = m.meal_id
WHERE ppm.meal_plan_id = ?
ORDER BY ppm.scheduled_datetime;


SELECT meal_plan_id FROM meal_plan WHERE user_id = ? AND title = ?;


DELETE FROM meal_plan_meal WHERE meal_plan_id = ?;


DELETE FROM meal_plan WHERE meal_plan_id = ?;


SELECT * FROM meal_plan where user_id = ?
ORDER BY meal_plan_id;


UPDATE meal_plan
  SET title = ?, start_date = ?, end_date = ?, goals = ?
WHERE meal_plan_id = ?;


UPDATE meal_plan_meal
SET scheduled_datetime = ?
WHERE meal_plan_id = ? and meal_id = ?;


DELETE FROM meal_plan_meal WHERE meal_plan_id = ? and meal_id = ?;
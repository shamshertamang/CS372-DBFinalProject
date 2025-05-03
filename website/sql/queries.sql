-- get user by email
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

-- get user by user_name
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

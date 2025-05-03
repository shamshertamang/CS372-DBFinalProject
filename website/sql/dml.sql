/*
 AI was used to generate this data
 */

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

/* ----------------------------------------------------------------
   USERS
   ---------------------------------------------------------------- */
INSERT INTO users (id, user_name, name, email, password, cooking_level, photo_data) VALUES
  (1, 'foodie_guru', 'Aarav Gurung',  'aarav@example.com',  'hashedpassword1', 4, NULL),
  (2, 'chef_emily',  'Emily Chen',    'emily@example.com',  'hashedpassword2', 3, NULL),
  (3, 'carlos_kitchen','Carlos Ruiz', 'carlos@example.com', 'hashedpassword3', 2, NULL),
  (4, 'bella_bites',  'Isabella Rossi','bella@example.com', 'hashedpassword4', 5, NULL);

/* ----------------------------------------------------------------
   DIETARY PREFERENCES & ALLERGIES
   ---------------------------------------------------------------- */
INSERT INTO user_dietary_preference (user_id, preference) VALUES
  (1,'Vegetarian'), (1,'Low Sugar'), (1,'High Protein'),
  (2,'Pescatarian'),
  (4,'Gluten-Free');

INSERT INTO user_allergy (user_id, allergy) VALUES
  (1,'Peanuts'), (1,'Shellfish'),
  (2,'Lactose'),
  (4,'Soy');

/* ----------------------------------------------------------------
   INGREDIENTS  (ids 1-56)
   ---------------------------------------------------------------- */
/* -- User 1 ingredients (ids 1-34) */
INSERT INTO ingredient (id,user_id,name,store,unit,seasonal_availability) VALUES
  (1,1,'Rice',NULL,'kg',NULL),
  (2,1,'Lentils',NULL,'g',NULL),
  (3,1,'Salt',NULL,'tsp',NULL),
  (4,1,'Flour',NULL,'g',NULL),
  (5,1,'Vegetable Filling',NULL,'g',NULL),
  (6,1,'Spices Mix',NULL,'tsp',NULL),
  (7,1,'Pizza Dough',NULL,'g',NULL),
  (8,1,'Tomato Sauce',NULL,'ml',NULL),
  (9,1,'Mozzarella',NULL,'g',NULL),
  (10,1,'Fresh Basil',NULL,'g',NULL),
  (11,1,'Sushi Rice',NULL,'g',NULL),
  (12,1,'Nori Sheets',NULL,'piece',NULL),
  (13,1,'Cucumber',NULL,'g',NULL),
  (14,1,'Avocado',NULL,'piece',NULL),
  (15,1,'Corn Tortilla',NULL,'piece',NULL),
  (16,1,'Pork',NULL,'g',NULL),
  (17,1,'Pineapple',NULL,'g',NULL),
  (18,1,'Chili Marinade',NULL,'ml',NULL),
  (19,1,'Rice Noodles',NULL,'g',NULL),
  (20,1,'Tofu',NULL,'g',NULL),
  (21,1,'Pad Thai Sauce',NULL,'ml',NULL),
  (22,1,'Chickpeas',NULL,'g',NULL),
  (23,1,'Pita Bread',NULL,'piece',NULL),
  (24,1,'Tahini Sauce',NULL,'ml',NULL),
  (25,1,'Mixed Vegetables',NULL,'g',NULL),
  (26,1,'Soy Sauce',NULL,'ml',NULL),
  (27,1,'Garlic',NULL,'clove',NULL),
  (28,1,'All-purpose Flour',NULL,'g',NULL),
  (29,1,'Milk',NULL,'ml',NULL),
  (30,1,'Eggs',NULL,'piece',NULL),
  (31,1,'Fresh Eggs',NULL,'piece',NULL),
  (32,1,'Tomatoes',NULL,'g',NULL),
  (33,1,'Bell Pepper',NULL,'g',NULL),
  (34,1,'Onion',NULL,'g',NULL);

/* -- User 2 ingredients (ids 35-41) */
INSERT INTO ingredient (id,user_id,name,store,unit) VALUES
  (35,2,'Salmon Fillet',NULL,'g'),
  (36,2,'Teriyaki Sauce',NULL,'ml'),
  (37,2,'Sesame Seeds',NULL,'g'),
  (38,2,'Feta Cheese',NULL,'g'),
  (39,2,'Cucumber',NULL,'g'),
  (40,2,'Olives',NULL,'g'),
  (41,2,'Olive Oil',NULL,'ml');

/* -- User 3 ingredients (ids 42-48) */
INSERT INTO ingredient (id,user_id,name,store,unit) VALUES
  (42,3,'Chicken Breast',NULL,'g'),
  (43,3,'Bell Pepper',NULL,'g'),
  (44,3,'Fajita Seasoning',NULL,'g'),
  (45,3,'Spaghetti',NULL,'g'),
  (46,3,'Bacon',NULL,'g'),
  (47,3,'Parmesan',NULL,'g'),
  (48,3,'Egg',NULL,'piece');

/* -- User 4 ingredients (ids 49-56) */
INSERT INTO ingredient (id,user_id,name,store,unit) VALUES
  (49,4,'Arborio Rice',NULL,'g'),
  (50,4,'Mushrooms',NULL,'g'),
  (51,4,'Vegetable Stock',NULL,'ml'),
  (52,4,'Parmesan',NULL,'g'),
  (53,4,'Tomato',NULL,'g'),
  (54,4,'Mozzarella',NULL,'g'),
  (55,4,'Fresh Basil',NULL,'g'),
  (56,4,'Olive Oil',NULL,'ml');

/* ----------------------------------------------------------------
   RECIPES  (ids 1-16)
   ---------------------------------------------------------------- */
/* -- 10 recipes for User 1 (includes 2 Nepali) */
INSERT INTO recipe (id,user_id,name,origin,difficulty,preparation_time,cooking_time,serving_size,source,photo)
VALUES
  (1,1,'Dal Bhat','Nepal',2,'20','30',4,'self',NULL),
  (2,1,'Momo','Nepal',3,'45','15',4,'self',NULL),
  (3,1,'Margherita Pizza','Italy',3,'30','15',2,'self',NULL),
  (4,1,'Sushi Rolls','Japan',4,'35','0',4,'self',NULL),
  (5,1,'Tacos al Pastor','Mexico',3,'25','15',4,'self',NULL),
  (6,1,'Pad Thai','Thailand',3,'20','15',2,'self',NULL),
  (7,1,'Falafel Wrap','Middle East',2,'15','10',2,'self',NULL),
  (8,1,'Vegetable Stir-Fry','China',1,'10','10',2,'self',NULL),
  (9,1,'French Crepes','France',2,'10','10',4,'self',NULL),
  (10,1,'Shakshuka','Israel',2,'15','15',3,'self',NULL);

/* -- 2 recipes each for Users 2-4 */
INSERT INTO recipe (id,user_id,name,origin,difficulty,preparation_time,cooking_time,serving_size,source,photo) VALUES
  (11,2,'Salmon Teriyaki','Japan',2,'10','15',2,'self',NULL),
  (12,2,'Greek Salad','Greece',1,'15','0',2,'self',NULL),
  (13,3,'Chicken Fajitas','Mexico',2,'20','15',3,'self',NULL),
  (14,3,'Pasta Carbonara','Italy',3,'10','15',2,'self',NULL),
  (15,4,'Risotto ai Funghi','Italy',4,'15','25',2,'self',NULL),
  (16,4,'Caprese Salad','Italy',1,'10','0',2,'self',NULL);

/* ----------------------------------------------------------------
   RECIPE_INGREDIENTS  (ids 1-56)
   ---------------------------------------------------------------- */
INSERT INTO recipe_ingredient (id,recipe_id,ingredient_id,quantity,unit) VALUES
  (1,1,1,'1','cup'),
  (2,1,2,'1','cup'),
  (3,1,3,'0','per taste'),
  (4,2,4,'2','cups'),
  (5,2,5,'1','cup'),
  (6,2,6,'1','tbsp'),
  (7,3,7,'250','g'),
  (8,3,8,'100','ml'),
  (9,3,9,'150','g'),
  (10,3,10,'5','g'),
  (11,4,11,'200','g'),
  (12,4,12,'3','piece'),
  (13,4,13,'50','g'),
  (14,4,14,'1','piece'),
  (15,5,15,'3','piece'),
  (16,5,16,'200','g'),
  (17,5,17,'50','g'),
  (18,5,18,'30','ml'),
  (19,6,19,'200','g'),
  (20,6,20,'100','g'),
  (21,6,21,'60','ml'),
  (22,7,22,'150','g'),
  (23,7,23,'2','piece'),
  (24,7,24,'30','ml'),
  (25,8,25,'200','g'),
  (26,8,26,'30','ml'),
  (27,8,27,'2','clove'),
  (28,9,28,'200','g'),
  (29,9,29,'300','ml'),
  (30,9,30,'2','piece'),
  (31,10,31,'4','piece'),
  (32,10,32,'400','g'),
  (33,10,33,'100','g'),
  (34,10,34,'1','piece'),
  (35,11,35,'250','g'),
  (36,11,36,'60','ml'),
  (37,11,37,'5','g'),
  (38,12,38,'100','g'),
  (39,12,39,'100','g'),
  (40,12,40,'30','g'),
  (41,12,41,'20','ml'),
  (42,13,42,'300','g'),
  (43,13,43,'150','g'),
  (44,13,44,'15','g'),
  (45,14,45,'200','g'),
  (46,14,46,'100','g'),
  (47,14,47,'50','g'),
  (48,14,48,'1','piece'),
  (49,15,49,'250','g'),
  (50,15,50,'150','g'),
  (51,15,51,'500','ml'),
  (52,15,52,'40','g'),
  (53,16,53,'200','g'),
  (54,16,54,'150','g'),
  (55,16,55,'5','g'),
  (56,16,56,'20','ml');

/* ----------------------------------------------------------------
   RECIPE_STEPS  (ids 1-48)  — 3 steps each recipe
   ---------------------------------------------------------------- */
INSERT INTO recipe_step (id,recipe_id,step_number,description) VALUES
  (1,1,1,'Rinse rice and lentils separately.'),
  (2,1,2,'Cook lentils with spices to make dal.'),
  (3,1,3,'Steam rice until fluffy and serve with dal.'),

  (4,2,1,'Prepare momo dough and let it rest.'),
  (5,2,2,'Mix vegetable filling with spices.'),
  (6,2,3,'Fill, fold, and steam momos.'),

  (7,3,1,'Stretch pizza dough on tray.'),
  (8,3,2,'Spread tomato sauce and add mozzarella.'),
  (9,3,3,'Bake and finish with fresh basil.'),

  (10,4,1,'Cook sushi rice and season.'),
  (11,4,2,'Place nori, spread rice, add fillings.'),
  (12,4,3,'Roll tightly and slice.'),

  (13,5,1,'Marinate pork with chili marinade.'),
  (14,5,2,'Grill pork and slice thinly.'),
  (15,5,3,'Assemble tacos with pineapple and pork.'),

  (16,6,1,'Soak rice noodles until soft.'),
  (17,6,2,'Stir-fry tofu and vegetables.'),
  (18,6,3,'Add noodles and Pad Thai sauce.'),

  (19,7,1,'Blend soaked chickpeas with herbs.'),
  (20,7,2,'Shape mixture into balls and fry.'),
  (21,7,3,'Wrap falafel in pita with tahini sauce.'),

  (22,8,1,'Heat wok and add oil.'),
  (23,8,2,'Stir-fry vegetables with garlic.'),
  (24,8,3,'Season with soy sauce and serve.'),

  (25,9,1,'Whisk flour, milk, and eggs into batter.'),
  (26,9,2,'Ladle batter onto hot pan, swirl thinly.'),
  (27,9,3,'Flip once edges lift; serve warm.'),

  (28,10,1,'Sauté onions and peppers until soft.'),
  (29,10,2,'Add tomatoes and simmer sauce.'),
  (30,10,3,'Poach eggs in sauce until set.'),

  (31,11,1,'Combine teriyaki sauce ingredients if homemade.'),
  (32,11,2,'Pan-sear salmon skin-side down.'),
  (33,11,3,'Glaze with teriyaki and sprinkle sesame.'),

  (34,12,1,'Chop vegetables into bite-size pieces.'),
  (35,12,2,'Add feta and olives.'),
  (36,12,3,'Dress with olive oil and season.'),

  (37,13,1,'Slice chicken and peppers.'),
  (38,13,2,'Sauté with fajita seasoning.'),
  (39,13,3,'Serve sizzling with tortillas.'),

  (40,14,1,'Cook spaghetti al dente.'),
  (41,14,2,'Sauté bacon until crisp.'),
  (42,14,3,'Toss pasta with eggs and parmesan off-heat.'),

  (43,15,1,'Toast rice in pan with oil.'),
  (44,15,2,'Add stock gradually, stirring constantly.'),
  (45,15,3,'Fold in mushrooms and parmesan at the end.'),

  (46,16,1,'Slice tomatoes and mozzarella.'),
  (47,16,2,'Layer alternately on plate.'),
  (48,16,3,'Drizzle with olive oil and garnish with basil.');

/* ----------------------------------------------------------------
   MEALS  (ids 1-9)
   ---------------------------------------------------------------- */
/* -- 6 meals for User 1 */
INSERT INTO meal (meal_id,meal_title,user_id,meal_time) VALUES
  (1,'Breakfast Day 1',1,'Breakfast'),
  (2,'Lunch Day 1',1,'Lunch'),
  (3,'Dinner Day 1',1,'Dinner'),
  (4,'Breakfast Day 2',1,'Breakfast'),
  (5,'Lunch Day 2',1,'Lunch'),
  (6,'Dinner Day 2',1,'Dinner');

/* -- 1 meal for each other user */
INSERT INTO meal (meal_id,meal_title,user_id,meal_time) VALUES
  (7,'Healthy Lunch',2,'Lunch'),
  (8,'Family Dinner',3,'Dinner'),
  (9,'Light Lunch',4,'Lunch');

/* ----------------------------------------------------------------
   MEAL_RECIPES  (link recipes to meals)
   ---------------------------------------------------------------- */
INSERT INTO meal_recipe (meal_id,recipe_id) VALUES
  (1,9),   -- French Crepes
  (2,1),   -- Dal Bhat
  (3,2),   -- Momo
  (4,10),  -- Shakshuka
  (5,6),   -- Pad Thai
  (6,5),   -- Tacos al Pastor
  (7,12),  -- Greek Salad
  (8,13),  -- Chicken Fajitas
  (9,16);  -- Caprese Salad

/* ----------------------------------------------------------------
   MEAL PLANS  (User 1 only)
   ---------------------------------------------------------------- */
INSERT INTO meal_plan (meal_plan_id,title,user_id,start_date,end_date,goals) VALUES
  (1,'Weekday Plan',1,'2025-05-01','2025-05-04','Balanced meals'),
  (2,'Weekend Plan',1,'2025-05-05','2025-05-08','Try international dishes');

/* Link meals to the plans with a schedule (Meal_plan_meal) */
INSERT INTO meal_plan_meal (meal_plan_id,meal_id,scheduled_datetime) VALUES
  -- Weekday Plan
  (1,1,'2025-05-02 08:00'),
  (1,2,'2025-05-02 12:30'),
  (1,3,'2025-05-02 19:00'),
  -- Weekend Plan
  (2,4,'2025-05-06 08:30'),
  (2,5,'2025-05-06 13:00'),
  (2,6,'2025-05-06 19:30');

COMMIT;
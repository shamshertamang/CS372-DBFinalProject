# Database Application Project Proposal

### Name
Shamsher

## Application Title

FoodBook - A Social Recipe App that allows users to save, share, plan and generate their recipes

## Application Purpose and Summary

FoodBook solves the challenging problem of meal planning and preparing, recipe organization and grocery shopping by providing a cutting edge platform for food enthusiasts and home cooks. The application allows users to create, discover and share recipes with their friends and family while automatically getting a list of ingredients and nutritional information about different recipes. The FoodBook pro also features the facility to generate a recipe at a cost of $1 for each recipe generated. This app is a great solution in bridging the disconnection between making meal plans, organizing grocery inventory and scheduling meal preps by offering a unified system that saves you from all the headaches, reduces food waste, simplifies grocery shopping process and promotes dietary awareness on different food recipes.

The upcoming version 2.0 of this app is aimed to intelligently give users tasks for meal prep by breaking down complex recipes into manageable optimised sequence of tasks making it seemless to make large meals reducing users' cooking time, so they can spend more quality time with your friends and family eating and laughing.

## Proposed Entities

Users: User profiles with their name, dietary preferances, cooking level, allergies and subscription status.

Ingredients: Name, Store, Common Substitutes and Seasonal Availability.

Recipe: contains preparation steps, cooking time, difficulty level, photos and tasks breakdown, reminders for marinations(before night) if applicable; can be saved

Meal plans: A list of meals for the week or interval of time with time and link to recipes

Pantry: Users can input the ingredients they already have and their shelf life. so they can make informed decision on grocery stocks to buy

Shopping List: Organised by store, based on meal plans and pantry

Recipe Collection: Based on Themes and Occassions

Meal Prep Tasks: [available for version 2] tasks will be organised by user or AI so that time can be saved while making huge dining plans

## Proposed Technology Stack

Programming Language: Python with Flask

Interactive UI/UX Approach: web interface using HTML/CSS

Database Type: SQLite

Other Frameworks and Tools: [maybe] Stripe API (for payments), Firebase (authentication and notifications)

## User Interaction for CRUD Operations

### Creating New Data:

Users can register for an account.

Users can create recipes through form with dynamic ingredient fields, step ordering, time and day, reminders and photo uploads.

The premium recipe generator will allow users to specify ingredients, dietary restrictions, and cooking time to receive AI-generated recipes for $1 each. 

Users can also create meal plans by dragging recipes onto a calendar interface, with the system automatically calculating prep time requirements and suggesting optimal cooking schedules.

[if I have time] the users can also share recipes with their friends.

### Viewing/Reading Existing Data:

The application supports a dashboard with personalised recipes, either created by user, generated through app or shared by connections.

Users can click on the recipe to see ingredients, instructions and times. The meal prep timeline also allows the user a visual schedule of when to perform specific task to maximize efficiency when preparing dishes.

### Updating Existing Data:

Users can update their profiles.

Users can modify their recipes.

The pantry will be updated dynamically as the meal prep is done.

Users can cross which meals/recipes have been prepared.

### Deleting Data:

Users can delete their accounts.

Recipes can be deleted.

The meals plans can be deleted. In this case, the shopping list is automatically updated.

## Maybe Additional Notes

Inter user messaging maybe be introduced so that users can text and share recipes
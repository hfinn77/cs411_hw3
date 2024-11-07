#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal, $cuisine, $price, $difficulty) to the database..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
  -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "combatant added"'

  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

delete_meal() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "meal deleted"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal=$1

  echo "Getting meal by name (Meal: '$meal')..."
  mll=$(echo $meal | sed 's/ /%20/g')
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$mll")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name."
    exit 1
  fi
}

############################################################
#
# Battle Management
#
############################################################

prep_combatant() {
  id=$1
  meal=$2
  price=$3
  cuisine=$4
  difficulty=$5
  
  echo "Prepping combatant '$Meal' for battle..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{ \"id\":\"$id\", \"meal\":\"$meal\", \"price\":\"$price\", \"cuisine\":\"$cuisine\", \"difficulty\":\"$difficulty\"}")

  if echo "$response" | grep -q '"status": "combatant prepared"'; then
    echo "Meal prepared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to prepare meal for battle."
    exit 1
  fi
}

battle() {

  echo "Battling..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  echo $response
  if echo "$response" | grep -q '"status": "battle complete"'; then
    echo "Battle has taken place"
  else
    echo "Failed to battle."
    exit 1
  fi
}


# Health checks
check_health
check_db

# Create meals
create_meal "Testing111" "Testing2" 5.00 "LOW"
create_meal "Meal2" "Cuisine 2" 10.0 "MED"
create_meal "Meal3" "Cuisine 3" 15.0 "HIGH"
create_meal "Meal4" "Cuisine 4" 7.5 "MED"
create_meal "Meal5" "Cuisine 5" 5.5 "LOW"

delete_meal 1
get_leaderboard

get_meal_by_id 2
get_meal_by_name "Meal5"

prep_combatant 2 "Meal2" "Cuisine 2" 10.0 "MED"
prep_combatant 3 "Meal3" "Cuisine 3" 15.0 "HIGH"

battle

echo "All tests passed successfully!"



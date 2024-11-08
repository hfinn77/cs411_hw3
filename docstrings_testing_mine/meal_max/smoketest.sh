#!/bin/bash

# smoketest.sh - Smoke test for Meal operations

# Define base URL for API endpoints
BASE_URL="http://localhost:5001/api"

# Flag to control JSON output
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
# Health check
#
###############################################

# Check API health
check_health() {
  echo "Checking API health..."
  response=$(curl -s -X GET "$BASE_URL/health")
  if echo "$response" | grep -q '"status": "healthy"'; then
    echo "API is healthy."
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
# Meal Management Functions
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

##########################################################
#
# Battle Management Functions
#
##########################################################

prep_combatant() {

  meal_name=$1
  cuisine=$2
  price=$3

  echo "Preparing combatant ($meal_name)..."

  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal_name\", \"cuisine\": \"$cuisine\", \"price\": $price}")
  

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
  echo "Testing battle endpoint..."
  response=$(curl -s -X GET "$BASE_URL/battle")
    echo "$response"

  if echo "$response" | grep -q '"status": "battle complete"'; then
    echo "Battle completed successfully."
  else
    echo "Battle test failed."
    exit 1
  fi

}

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")
  if echo "$response" | grep -q '"status": "combatants cleared"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi

}

##########################################################
#
# Leaderboard
#
##########################################################

get_leaderboard() {

  if [ $# -eq 0 ]; then
    param="wins"
  else
    param=$1
  fi

  echo "Retrieving leaderboard sorted by $param..."

  response=$(curl -s -X GET "$BASE_URL/leaderboard" -H "Content-Type: application/json" \
    -d "{\"sort_by\": \"$param\"}")

  echo "$response"

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}







##########################################################
#
# Execute Tests
#
##########################################################

# Health check
check_health
check_db

# Create meals
create_meal "Spaghetti" "Italian" 12.5 "MED"
create_meal "Sushi" "Japanese" 15.0 "HIGH"
create_meal "Pizza" "Italian" 3.0 "MED"
create_meal "Fries" "France" 4.0 "LOW"

# Prep compatant
prep_combatant "Spaghetti" "Italian" 12.5
prep_combatant "Sushi" "Japanese" 15.0


# Retrieve meals by ID and by name
get_meal_by_id 1
get_meal_by_name "Spaghetti"

# Battle
battle 

# Clear combatants 
clear_combatants

# Another battle
prep_combatant "Pizza" "Italian" 3.0
prep_combatant "Sushi" "Japanese" 15.0

battle 

# Retrieve leaderboard
get_leaderboard "wins"
get_leaderboard "win_pct"

# Delete meal
delete_meal 1


echo "All smoke tests completed successfully!"


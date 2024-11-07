#!/bin/bash

<<<<<<< HEAD
# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
=======
# smoketest.sh - Smoke test for Meal operations

# Define base URL for API endpoints
BASE_URL="http://localhost:5000/api"

# Flag to control JSON output
>>>>>>> 694a1d6 (added more smoketests)
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
<<<<<<< HEAD
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
=======
# Health check
#
###############################################

# Check API health
check_health() {
  echo "Checking API health..."
  response=$(curl -s -X GET "$BASE_URL/health")
  if echo "$response" | grep -q '"status": "healthy"'; then
    echo "API is healthy."
>>>>>>> 694a1d6 (added more smoketests)
  else
    echo "Health check failed."
    exit 1
  fi
}

<<<<<<< HEAD
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
=======

##########################################################
#
# Meal Management Functions
>>>>>>> 694a1d6 (added more smoketests)
#
##########################################################

create_meal() {
<<<<<<< HEAD
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
=======
  local meal_name=$1
  local cuisine=$2
  local price=$3
  local difficulty=$4

  echo "Creating meal ($meal_name, $cuisine, $price, $difficulty)..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal_name\", \"cuisine\": \"$cuisine\", \"price\": $price, \"difficulty\": \"$difficulty\"}")

  if echo "$response" | grep -q '"status": "combatant added"'; then
    echo "Meal created successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to create meal."
>>>>>>> 694a1d6 (added more smoketests)
    exit 1
  fi
}

delete_meal() {
<<<<<<< HEAD
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "meal deleted"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
=======
  local meal_id=$1

  echo "Deleting meal with ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")

  if echo "$response" | grep -q '"status": "meal deleted"'; then
    echo "Meal deleted successfully."
  else
    echo "Failed to delete meal."
>>>>>>> 694a1d6 (added more smoketests)
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

<<<<<<< HEAD
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
=======
  echo "Retrieving meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully."
>>>>>>> 694a1d6 (added more smoketests)
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
<<<<<<< HEAD
    echo "Failed to prepare meal for battle."
=======
    echo "Failed to retrieve meal by ID."
>>>>>>> 694a1d6 (added more smoketests)
    exit 1
  fi
}

<<<<<<< HEAD
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


=======
get_meal_by_name() {
  local meal_name=$1

  echo "Retrieving meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve meal by name."
    exit 1
  fi
}

get_leaderboard() {

  echo "Retrieving leaderboard sorted by wins..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")

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

prep_combatant() {

  local meal_name=$1
  local cuisine=$2
  local price=$3

  echo "Preparing combatant ($meal_name)..."

  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal_name\", \"cuisine\": \"$cuisine\", \"price\": $price}")
  

  if echo "$response" | grep -q '"status": "combatant prepared"'; then
    if ["$ECHO_JSON" = true]; then
      echo "Combatant JSON (meal $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to prepare combatant."
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
# Execute Tests
#
##########################################################

# Health check
check_health

# Create meals
create_meal "Spaghetti" "Italian" 12.5 "MED"
create_meal "Sushi" "Japanese" 15.0 "HIGH"

# Prep compatant
prep_combatant "Spaghetti" "Italian" 12.5
prep_combatant "Sushi" "Japanese" 15.0


# Retrieve meals by ID and by name
get_meal_by_id 1
get_meal_by_name "Spaghetti"

# Battle
battle 

# Retrieve leaderboard
get_leaderboard "wins"
get_leaderboard "win_pct"

# Clear combatants 
clear_combatants

# Delete meal
delete_meal 1


echo "All smoke tests completed successfully!"
>>>>>>> 694a1d6 (added more smoketests)

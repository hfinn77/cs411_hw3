#!/bin/bash

# smoketest.sh - Smoke test for Meal operations

# Define base URL for API endpoints
BASE_URL="http://localhost:5000/api"

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


##########################################################
#
# Meal Management Functions
#
##########################################################

create_meal() {
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
    exit 1
  fi
}

delete_meal() {
  local meal_id=$1

  echo "Deleting meal with ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")

  if echo "$response" | grep -q '"status": "meal deleted"'; then
    echo "Meal deleted successfully."
  else
    echo "Failed to delete meal."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Retrieving meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve meal by ID."
    exit 1
  fi
}

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


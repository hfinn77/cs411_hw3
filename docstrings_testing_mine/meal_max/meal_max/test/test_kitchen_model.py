#tests

from contextlib import contextmanager
import re
import sqlite3

import pytest 

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

##################################################
# Create Meal Test Cases
##################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the database."""

    # Call the function to create a new meal
    create_meal(meal='Meal 1', cuisine='Cuisine 1', price=5.00, difficulty='LOW')

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ('Meal 1', 'Cuisine 1', 5.00, 'LOW')
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (e.g., negative duration)"""

    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -5.0. Price must be a positive number."):
        create_meal(meal='Meal 1', cuisine='Cuisine 1', price=-5.00, difficulty='LOW')

    # Attempt to create a meal with a non-integer price
    with pytest.raises(ValueError, match="Invalid price: 5.00. Price must be a positive number."):
        create_meal(meal='Meal 1', cuisine='Cuisine 1', price="5.00", difficulty='LOW')

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (not in [LOW, MED, HIGH])"""

    # Attempt to create a meal with an invalid difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: IMPOSSIBLE. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal='Meal 1', cuisine='Cuisine 1', price=5.00, difficulty='IMPOSSIBLE')

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the catalog by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_meal function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

def test_get_leaderboard(mock_cursor):
    """Test retrieving all meals that are not marked as deleted."""

    # Simulate that there are multiple meals in the database
    mock_cursor.fetchall.return_value = [
        (1, 'Meal 1', 'Cuisine 1', 5.00, 'LOW', 3, 3, 1),
        (2, 'Meal 2', 'Cuisine 2', 10.00, 'MED', 2, 1, 0.5),
        (3, 'Meal 3', 'Cuisine 3', 15.00, 'HIGH', 3, 0, 0),
    ]

    # Call the get_leaderboard function
    meals = get_leaderboard()

    # Ensure the results match the expected output
    expected_result = [
        {'id': 1, 'meal': 'Meal 1', 'cuisine': 'Cuisine 1', 'price': 5.0, 'difficulty': 'LOW', 'battles': 3, 'wins': 3, 'win_pct': 100}, 
        {'id': 2, 'meal': 'Meal 2', 'cuisine': 'Cuisine 2', 'price': 10.0, 'difficulty': 'MED', 'battles': 2, 'wins': 1, 'win_pct': 50.0}, 
        {'id': 3, 'meal': 'Meal 3', 'cuisine': 'Cuisine 3', 'price': 15.0, 'difficulty': 'HIGH', 'battles': 3, 'wins': 0, 'win_pct': 0}
        ]

    # print("meals:", meals)
    # print("eeals:", expected_result)
    assert meals == expected_result, f"Expected {expected_result}, but got {meals}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct 
        FROM meals 
        WHERE deleted = false AND battles > 0 ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # print("e:", expected_query)
    # print("a:", actual_query)

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_invalid_sort_by(mock_cursor):
    """Test retrieving all meals that are not marked as deleted."""

    # Simulate that there are multiple meals in the database
    mock_cursor.fetchall.return_value = [
        (1, 'Meal 1', 'Cuisine 1', 5.00, 'LOW', 3, 3, 1),
        (2, 'Meal 2', 'Cuisine 2', 10.00, 'MED', 2, 1, 0.5),
        (3, 'Meal 3', 'Cuisine 3', 15.00, 'HIGH', 3, 0, 0),
    ]

    # Call the get_leaderboard function
    with pytest.raises(ValueError, match="Invalid sort_by parameter: price"):
        meals = get_leaderboard(sort_by="price")

def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, 'Meal 1', 'Cuisine 1', 5.00, 'LOW', False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, 'Meal 1', 'Cuisine 1', 5.00, 'LOW')

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    print(actual_query)

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_id_deleted_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, 'Meal 1', 'Cuisine 1', 5.00, 'LOW', True)

    # Call the function and check the result
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        result = get_meal_by_id(1)

    
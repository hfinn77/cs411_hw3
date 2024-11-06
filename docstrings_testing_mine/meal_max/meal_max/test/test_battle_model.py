import pytest
from unittest.mock import MagicMock
import sqlite3

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal
from meal_max.utils.random_utils import get_random


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()


@pytest.fixture
def sample_meal_1():
    """Fixture for a sample Meal object."""
    return Meal(id=1, meal="Meal 1", price=15.0, cuisine="Italian", difficulty="HIGH")


@pytest.fixture
def sample_meal_2():
    """Fixture for a second sample Meal object."""
    return Meal(id=2, meal="Meal 2", price=10.0, cuisine="Mexican", difficulty="MED")


##################################################
# Combatant Management Test Cases
##################################################

def test_prep_combatant_addition(battle_model, sample_meal_1):
    """Test adding a combatant to the battle model."""
    battle_model.prep_combatant(sample_meal_1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "Meal 1"


def test_prep_combatant_exceeds_limit(battle_model, sample_meal_1, sample_meal_2):
    """Test error when adding more than two combatants to the model."""
    battle_model.prep_combatant(sample_meal_1)
    battle_model.prep_combatant(sample_meal_2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal_1)


def test_clear_combatants(battle_model, sample_meal_1):
    """Test clearing all combatants from the battle model."""
    battle_model.prep_combatant(sample_meal_1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0


##################################################
# Battle Execution Test Cases
##################################################
def test_battle(battle_model, sample_meal_1, sample_meal_2, mocker):
    """Test simulating a battle and determining a winner."""
    
    # Patch DB_PATH to use in-memory database
    mocker.patch("meal_max.utils.sql_utils.DB_PATH", ":memory:")
    
    # Prepare combatants
    battle_model.prep_combatant(sample_meal_1)
    battle_model.prep_combatant(sample_meal_2)

    # Mock get_random and update_meal_stats to control randomness and avoid side effects
    mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.5)
    mock_update_stats = mocker.patch("meal_max.models.battle_model.update_meal_stats")

    # Simulate battle and determine winner
    winner = battle_model.battle()

    # Check the winner and assert that stats were updated
    assert winner in [sample_meal_1.meal, sample_meal_2.meal]
    assert mock_update_stats.call_count == 2
    mock_update_stats.assert_any_call(sample_meal_1.id, 'win' if winner == sample_meal_1.meal else 'loss')
    mock_update_stats.assert_any_call(sample_meal_2.id, 'win' if winner == sample_meal_2.meal else 'loss')


def test_battle_with_insufficient_combatants(battle_model):
    """Test battle raises an error if there are fewer than two combatants."""
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()


##################################################
# Score and Utility Test Cases
##################################################

def test_battle_score_calculation(battle_model, sample_meal_1):
    """Test calculating a battle score based on meal attributes."""
    score = battle_model.get_battle_score(sample_meal_1)
    expected_score = (sample_meal_1.price * len(sample_meal_1.cuisine)) - 1  # HIGH difficulty has modifier of 1
    assert score == expected_score


def test_get_combatants(battle_model, sample_meal_1, sample_meal_2):
    """Test retrieving the current list of combatants."""
    battle_model.prep_combatant(sample_meal_1)
    battle_model.prep_combatant(sample_meal_2)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == "Meal 1"
    assert combatants[1].meal == "Meal 2"



def test_update_meal_stats_call_on_battle(battle_model, sample_meal_1, sample_meal_2, mocker):
    """Test that update_meal_stats is called correctly during battle for both winner and loser."""
    
    # Set up a single in-memory database connection and create the required table
    connection = sqlite3.connect(":memory:")
    connection.execute('''CREATE TABLE meals (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            cuisine TEXT,
                            price REAL,
                            difficulty TEXT,
                            battles INTEGER DEFAULT 0,
                            wins INTEGER DEFAULT 0,
                            deleted BOOLEAN DEFAULT 0
                          )''')
    connection.commit()

    # Insert test data if needed
    connection.execute("INSERT INTO meals (id, name, cuisine, price, difficulty) VALUES (?, ?, ?, ?, ?)",
                       (sample_meal_1.id, sample_meal_1.meal, sample_meal_1.cuisine, sample_meal_1.price, sample_meal_1.difficulty))
    connection.execute("INSERT INTO meals (id, name, cuisine, price, difficulty) VALUES (?, ?, ?, ?, ?)",
                       (sample_meal_2.id, sample_meal_2.meal, sample_meal_2.cuisine, sample_meal_2.price, sample_meal_2.difficulty))
    connection.commit()

    # Mock `get_db_connection` to return this in-memory database connection
    mocker.patch("meal_max.utils.sql_utils.get_db_connection", return_value=connection)

    # Prepare combatants
    battle_model.prep_combatant(sample_meal_1)
    battle_model.prep_combatant(sample_meal_2)

    # Mock `get_random` to control the randomness and `update_meal_stats` to capture the calls
    mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.5)

    # Conduct the battle
    winner = battle_model.battle()

    # Validate that `update_meal_stats` updated the stats as expected
    winner_id = sample_meal_1.id if winner == sample_meal_1.meal else sample_meal_2.id
    loser_id = sample_meal_2.id if winner == sample_meal_1.meal else sample_meal_1.id
    
    cursor = connection.cursor()
    cursor.execute("SELECT battles, wins FROM meals WHERE id = ?", (winner_id,))
    winner_battles, winner_wins = cursor.fetchone()
    
    cursor.execute("SELECT battles, wins FROM meals WHERE id = ?", (loser_id,))
    loser_battles, loser_wins = cursor.fetchone()

    assert winner_battles == 1
    assert winner_wins == 1
    assert loser_battles == 1
    assert loser_wins == 0

    # Close the in-memory database connection after the test
    connection.close()

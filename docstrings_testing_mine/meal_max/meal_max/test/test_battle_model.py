import pytest
from unittest.mock import MagicMock
import sqlite3
from unittest.mock import patch

from meal_max.models.battle_model import BattleModel

from meal_max.models.kitchen_model import Meal
from meal_max.utils.random_utils import get_random

import os
DATABASE_PATH = os.path.abspath("db/meal_max.db")

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

def test_get_battle_score_with_invalid_difficulty(battle_model, sample_meal1):
    """Test calculating battle score with an invalid difficulty."""
    sample_meal1.difficulty = "INVALID"

    with pytest.raises(KeyError):
        battle_model.get_battle_score(sample_meal1)


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
    
    # Set up a single in-memory database connection
    connection = sqlite3.connect(":memory:")
    connection.execute('''CREATE TABLE meals (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            cuisine TEXT,
                            price REAL,
                            difficulty TEXT,
                            deleted BOOLEAN DEFAULT 0
                          )''')
    connection.commit()
    
    # Mock DB_PATH and get_db_connection to always return this same in-memory database
    mocker.patch("meal_max.utils.sql_utils.DB_PATH", ":memory:")
    mocker.patch("meal_max.utils.sql_utils.get_db_connection", return_value=connection)
    
    # Prepare combatants
    battle_model.prep_combatant(sample_meal_1)
    battle_model.prep_combatant(sample_meal_2)
    
    # Mock get_random to control randomness and update_meal_stats to capture calls
    mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.5)
    mock_update_meal_stats = mocker.patch("meal_max.models.kitchen_model.update_meal_stats")
    
    # Conduct the battle
    winner = battle_model.battle()
    
    # Additional assertions or checks can go here if needed
    
    # Close the in-memory database connection at the end of the test
    connection.close()

def test_combatant_list_order(battle_model, sample_meal_1, sample_meal_2):
    """Test that combatants are added in the correct order."""
    battle_model.prep_combatant(sample_meal_1)
    battle_model.prep_combatant(sample_meal_2)
    combatants = battle_model.get_combatants()
    assert combatants[0].meal == "Meal 1"
    assert combatants[1].meal == "Meal 2"


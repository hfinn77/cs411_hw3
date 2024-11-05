import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal
from meal_max.utils.random_utils import get_random

@pytest.fixture
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_meal1():
    """Fixture to provide a sample meal for testing."""
    return Meal(id=1, meal="Meal 1", price=10.0, cuisine="Italian", difficulty="HIGH")

@pytest.fixture
def sample_meal2():
    """Fixture to provide a second sample meal for testing."""
    return Meal(id=2, meal="Meal 2", price=15.0, cuisine="Chinese", difficulty="MED")

@pytest.fixture
def sample_combatants(sample_meal1, sample_meal2):
    """Fixture to provide a list of two sample meals for battle testing."""
    return [sample_meal1, sample_meal2]

##################################################
# Battle Functionality Test Cases
##################################################

def test_battle(monkeypatch, battle_model, sample_combatants):
    """Test conducting a battle and verifying the winner and stats update."""
    # Mock get_random to return 0.5
    monkeypatch.setattr("meal_max.utils.random_utils.get_random", lambda: 0.5)

    # Mock update_meal_stats to verify it's called correctly
    update_stats_calls = []
    def mock_update_meal_stats(meal_id, result):
        update_stats_calls.append((meal_id, result))
    monkeypatch.setattr("meal_max.models.kitchen_model.update_meal_stats", mock_update_meal_stats)

    # Set combatants and run the battle
    battle_model.combatants.extend(sample_combatants)
    winner = battle_model.battle()

    # Check that the winner's meal name is returned
    assert winner in ["Meal 1", "Meal 2"], f"Unexpected winner: {winner}"

    # Ensure stats are updated for both combatants
    assert update_stats_calls == [
        (sample_combatants[0].id, 'win'),
        (sample_combatants[1].id, 'loss')
    ]

def test_battle_insufficient_combatants(battle_model, sample_meal1):
    """Test that starting a battle with fewer than two combatants raises an error."""
    battle_model.combatants.append(sample_meal1)
    
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

##################################################
# Combatant Management Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1, sample_meal2):
    """Test adding combatants and enforcing a two-combatant limit."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.combatants) == 2, "Expected two combatants in the list"
    
    # Test adding a third combatant raises an error
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(Meal(id=3, meal="Meal 3", price=12.0, cuisine="Mexican", difficulty="LOW"))

def test_clear_combatants(battle_model, sample_combatants):
    """Test clearing the combatants list."""
    battle_model.combatants.extend(sample_combatants)
    battle_model.clear_combatants()
    assert battle_model.combatants == [], "Expected combatants list to be empty after clearing"

##################################################
# Battle Score Calculation Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test calculating the battle score for a combatant based on its attributes."""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 1  # Assuming HIGH difficulty has modifier 1
    assert score == pytest.approx(expected_score, rel=1e-3), f"Expected score: {expected_score}, got: {score}"

##################################################
# Combatants Retrieval Test Cases
##################################################

def test_get_combatants(battle_model, sample_combatants):
    """Test retrieving the current list of combatants."""
    battle_model.combatants.extend(sample_combatants)
    retrieved_combatants = battle_model.get_combatants()
    assert len(retrieved_combatants) == 2, f"Expected 2 combatants, got {len(retrieved_combatants)}"
    assert retrieved_combatants[0].meal == "Meal 1"
    assert retrieved_combatants[1].meal == "Meal 2"
import pytest
from unittest.mock import patch
from requests.exceptions import Timeout, RequestException
from meal_max.utils.random_utils import get_random

# Scenario 1: Test successful response with a valid random number
@patch("requests.get")
def test_get_random_success(mock_get):
    # Mock the response of requests.get
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "0.67"
    
    # Call the function and verify the output
    result = get_random()
    assert result == 0.67


# Scenario 2: Test invalid response format (cannot convert to float)
@patch("requests.get")
def test_get_random_invalid_format(mock_get):
    # Mock the response of requests.get to return an invalid format
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "invalid_number"
    
    # Call the function and expect a ValueError
    with pytest.raises(ValueError, match="Invalid response from random.org"):
        get_random()


# Scenario 3: Test timeout exception
@patch("requests.get", side_effect=Timeout)
def test_get_random_timeout(mock_get):
    # Call the function and expect a RuntimeError due to timeout
    with pytest.raises(RuntimeError, match="Request to random.org timed out"):
        get_random()


# Scenario 4: Test general request failure
@patch("requests.get", side_effect=RequestException("Network error"))
def test_get_random_request_failure(mock_get):
    # Call the function and expect a RuntimeError due to request failure
    with pytest.raises(RuntimeError, match="Request to random.org failed: Network error"):
        get_random()

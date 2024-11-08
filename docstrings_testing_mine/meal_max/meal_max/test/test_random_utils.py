import pytest
from unittest.mock import patch
from requests.exceptions import Timeout, RequestException
from meal_max.utils.random_utils import get_random

@patch("requests.get")
def test_get_random_success(mock_get):
    # Mock the response of requests.get
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "0.67"
    
    # Call the function and verify the output
    result = get_random()
    assert result == 0.67

@patch("requests.get")
def test_get_random_invalid_format(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "invalid_number"
    
    with pytest.raises(ValueError, match="Invalid response from random.org"):
        get_random()

@patch("requests.get", side_effect=Timeout)
def test_get_random_timeout(mock_get):

    with pytest.raises(RuntimeError, match="Request to random.org timed out"):
        get_random()

@patch("requests.get", side_effect=RequestException("Network error"))
def test_get_random_request_failure(mock_get):

    with pytest.raises(RuntimeError, match="Request to random.org failed: Network error"):
        get_random()

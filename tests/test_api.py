"""Tests for API integration."""
import pytest
from unittest.mock import patch, MagicMock
from utils.india_jobs_api import fetch_india_jobs


def test_fetch_india_jobs_success(mock_adzuna_response, env_vars):
    """Test successful job fetching."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_adzuna_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        jobs = fetch_india_jobs("data analyst", "India")
        
        assert len(jobs) > 0
        assert jobs[0]['MatchedObjectDescriptor']['PositionTitle'] == 'Data Analyst'


def test_fetch_india_jobs_no_results(env_vars):
    """Test when no jobs found."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        jobs = fetch_india_jobs("xyz random job", "xyz location")
        
        assert len(jobs) == 0


def test_fetch_india_jobs_api_error(env_vars):
    """Test API error handling."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API connection failed")
        
        with pytest.raises(Exception):
            fetch_india_jobs("data analyst", "India")

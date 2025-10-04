"""
Test configuration and utilities for Reviews Copilot backend tests.

This module provides common test utilities, fixtures, and configuration
to ensure consistent and comprehensive testing across all test modules.
"""

import pytest
import logging
from fastapi.testclient import TestClient
from app.main import app

# Configure test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tests.log')
    ]
)

logger = logging.getLogger(__name__)

@pytest.fixture
def client():
    """Provide a test client for FastAPI application"""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Provide authentication headers for API requests"""
    return {'x-api-key': 'supersecret'}

@pytest.fixture
def sample_reviews():
    """Provide sample review data for testing"""
    return [
        {
            "id": 1001,
            "location": "NYC - Manhattan",
            "rating": 5,
            "text": "Absolutely amazing food and service! The pasta was perfectly cooked and the staff was incredibly attentive.",
            "date": "2025-09-01"
        },
        {
            "id": 1002,
            "location": "Boston - Back Bay",
            "rating": 2,
            "text": "Very disappointing experience. The food was cold when it arrived and service was extremely slow.",
            "date": "2025-09-02"
        },
        {
            "id": 1003,
            "location": "Chicago - Loop",
            "rating": 4,
            "text": "Good atmosphere and decent food. The drinks were excellent but the entrees were just okay.",
            "date": "2025-09-03"
        },
        {
            "id": 1004,
            "location": "San Francisco - Mission",
            "rating": 1,
            "text": "Worst restaurant experience ever. Rude staff, terrible food, and overpriced. Would not recommend.",
            "date": "2025-09-04"
        },
        {
            "id": 1005,
            "location": "NYC - Brooklyn",
            "rating": 3,
            "text": "Average place. Nothing special but nothing terrible either. Okay for a quick meal.",
            "date": "2025-09-05"
        }
    ]

@pytest.fixture
def negative_review():
    """Provide a sample negative review for testing AI features"""
    return {
        "id": 2001,
        "location": "Test Location",
        "rating": 1,
        "text": "Terrible food quality, very slow service, and the restaurant was dirty. Complete waste of money.",
        "date": "2025-09-10"
    }

@pytest.fixture
def positive_review():
    """Provide a sample positive review for testing AI features"""
    return {
        "id": 2002,
        "location": "Test Location",
        "rating": 5,
        "text": "Outstanding experience! Delicious food, excellent service, and beautiful ambiance. Highly recommended!",
        "date": "2025-09-10"
    }

class TestHelper:
    """Helper class for common test operations"""
    
    @staticmethod
    def ingest_reviews(client, reviews, auth_headers, enrich=False):
        """Helper method to ingest reviews and return response"""
        logger.info(f"Ingesting {len(reviews)} reviews (enrich={enrich})")
        response = client.post('/ingest', 
                             json=reviews, 
                             headers=auth_headers, 
                             params={'enrich': enrich})
        logger.info(f"Ingestion response: {response.status_code}")
        return response
    
    @staticmethod
    def get_review(client, review_id, auth_headers):
        """Helper method to fetch a single review"""
        response = client.get(f'/reviews/{review_id}', headers=auth_headers)
        return response
    
    @staticmethod
    def suggest_reply(client, review_id, auth_headers, temperature=0.2):
        """Helper method to get AI reply suggestion"""
        response = client.post(f'/reviews/{review_id}/suggest-reply',
                             json={'temperature': temperature},
                             headers=auth_headers)
        return response
    
    @staticmethod
    def verify_ai_response(response_data):
        """Helper method to verify AI response structure"""
        assert 'reply' in response_data, "AI response missing 'reply'"
        assert 'tags' in response_data, "AI response missing 'tags'"
        assert 'reasoning_log' in response_data, "AI response missing 'reasoning_log'"
        assert 'sentiment' in response_data['tags'], "AI response missing sentiment"
        assert 'topic' in response_data['tags'], "AI response missing topic"
        assert isinstance(response_data['reasoning_log'], list), "reasoning_log should be list"
        
    @staticmethod
    def verify_pagination_response(response_data):
        """Helper method to verify pagination response structure"""
        assert 'reviews' in response_data, "Pagination response missing 'reviews'"
        assert 'pagination' in response_data, "Pagination response missing 'pagination'"
        assert isinstance(response_data['reviews'], list), "Reviews should be list"
        assert isinstance(response_data['pagination'], dict), "Pagination should be dict"

# Pytest markers for test organization
pytestmark = pytest.mark.integration
from fastapi.testclient import TestClient
from app.main import app
import pytest
import logging
import time

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_suggest_reply():
    """Test AI reply suggestion endpoint with three-tier fallback system"""
    logger.info("=== Starting AI Reply Suggestion Test ===")
    
    # First ingest a review
    test_review = {
        "id": 999, 
        "location": "TestCity", 
        "rating": 5, 
        "text": "Amazing service and delicious food!", 
        "date": "2025-09-10"
    }
    logger.info(f"Ingesting test review: {test_review}")
    
    ingest_res = client.post('/ingest', json=[test_review], headers={'x-api-key':'supersecret'}, params={'enrich': False})
    assert ingest_res.status_code == 200
    logger.info("Review ingested successfully")
    
    # Test suggest reply with timing
    logger.info("Testing AI reply suggestion...")
    start_time = time.time()
    
    res = client.post(
        '/reviews/999/suggest-reply',
        json={'temperature': 0.2},
        headers={'x-api-key':'supersecret'}
    )
    
    response_time = time.time() - start_time
    logger.info(f"Reply generation took {response_time:.2f} seconds")
    
    assert res.status_code == 200
    data = res.json()
    
    # Log the complete response for debugging
    logger.info(f"Response: {data}")
    
    # Verify response structure
    assert 'reply' in data, "Response missing 'reply' field"
    assert 'tags' in data, "Response missing 'tags' field"
    assert 'reasoning_log' in data, "Response missing 'reasoning_log' field"
    assert 'sentiment' in data['tags'], "Response missing sentiment tag"
    assert 'topic' in data['tags'], "Response missing topic tag"
    assert isinstance(data['reasoning_log'], list), "reasoning_log should be a list"
    
    # Verify the three-tier system is working
    reasoning = data['reasoning_log']
    logger.info(f"AI reasoning log: {reasoning}")
    
    # Should contain one of our fallback messages
    fallback_messages = [
        "Generated using OpenAI GPT-3.5-turbo",
        "Generated using DialoGPT-small fallback due to OpenAI failure", 
        "Generated using DialoGPT-small (OpenAI not available)",
        "Generated using template fallback due to both OpenAI and LLM failure",
        "Generated using template (both OpenAI and LLM not available)"
    ]
    
    assert any(msg in reasoning for msg in fallback_messages), f"No valid fallback message found in: {reasoning}"
    
    # Verify reply is not empty and reasonable length
    assert len(data['reply']) > 5, "Reply too short"
    assert len(data['reply']) < 500, "Reply too long"
    
    logger.info(f"✅ AI reply test passed - Generated: '{data['reply'][:50]}...'")
    logger.info("=== AI Reply Suggestion Test Complete ===\n")

def test_suggest_reply_not_found():
    """Test suggest reply for non-existent review"""
    logger.info("=== Testing Reply for Non-existent Review ===")
    
    non_existent_id = 99999
    logger.info(f"Attempting to generate reply for non-existent review ID: {non_existent_id}")
    
    res = client.post(
        f'/reviews/{non_existent_id}/suggest-reply',
        json={},
        headers={'x-api-key':'supersecret'}
    )
    
    logger.info(f"Response status: {res.status_code}")
    logger.info(f"Response body: {res.json()}")
    
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"
    
    response_data = res.json()
    assert 'detail' in response_data, "404 response should contain 'detail' field"
    
    logger.info("✅ Non-existent review test passed")
    logger.info("=== Non-existent Review Test Complete ===\n")

def test_analytics_with_topics():
    """Test analytics endpoint includes topics and comprehensive data"""
    logger.info("=== Testing Analytics Endpoint ===")
    
    # First ensure we have some data
    logger.info("Ingesting test data for analytics...")
    test_reviews = [
        {"id": 1001, "location": "NYC", "rating": 5, "text": "Great food and service!", "date": "2025-09-10"},
        {"id": 1002, "location": "Boston", "rating": 2, "text": "Poor service, slow staff", "date": "2025-09-11"},
        {"id": 1003, "location": "NYC", "rating": 4, "text": "Nice ambience, good drinks", "date": "2025-09-12"}
    ]
    
    ingest_res = client.post('/ingest', json=test_reviews, headers={'x-api-key':'supersecret'}, params={'enrich': False})
    assert ingest_res.status_code == 200
    logger.info("Test data ingested successfully")
    
    # Test analytics endpoint
    logger.info("Fetching analytics data...")
    res = client.get('/analytics', headers={'x-api-key':'supersecret'})
    
    assert res.status_code == 200, f"Analytics endpoint failed with status {res.status_code}"
    data = res.json()
    
    logger.info(f"Analytics response: {data}")
    
    # Verify all required fields are present
    required_fields = ['total', 'sentiment_counts', 'topic_counts', 'location_counts', 'rating_distribution', 'average_rating']
    for field in required_fields:
        assert field in data, f"Analytics response missing required field: {field}"
    
    # Verify data types and reasonable values
    assert isinstance(data['total'], int), "total should be an integer"
    assert data['total'] >= 3, f"Expected at least 3 reviews, got {data['total']}"
    
    assert isinstance(data['sentiment_counts'], dict), "sentiment_counts should be a dict"
    assert isinstance(data['topic_counts'], dict), "topic_counts should be a dict"
    assert isinstance(data['location_counts'], dict), "location_counts should be a dict"
    assert isinstance(data['rating_distribution'], dict), "rating_distribution should be a dict"
    
    assert isinstance(data['average_rating'], (int, float)), "average_rating should be numeric"
    assert 1.0 <= data['average_rating'] <= 5.0, f"average_rating should be 1-5, got {data['average_rating']}"
    
    # Verify location data
    assert 'NYC' in data['location_counts'], "Should have NYC in location counts"
    assert 'Boston' in data['location_counts'], "Should have Boston in location counts"
    
    logger.info(f"✅ Analytics test passed - Total reviews: {data['total']}, Avg rating: {data['average_rating']}")
    logger.info("=== Analytics Test Complete ===\n")

def test_ingest_with_enrichment():
    """Test ingestion with AI enrichment using fallback system"""
    logger.info("=== Testing AI Enrichment During Ingestion ===")
    
    # Test with a clearly negative review
    test_review = {
        "id": 1000, 
        "location": "NYC", 
        "rating": 1, 
        "text": "Terrible experience, very slow service and cold food", 
        "date": "2025-09-10"
    }
    
    logger.info(f"Ingesting review with enrichment: {test_review}")
    
    start_time = time.time()
    res = client.post('/ingest?enrich=true', json=[test_review], headers={'x-api-key':'supersecret'})
    enrichment_time = time.time() - start_time
    
    logger.info(f"Enrichment process took {enrichment_time:.2f} seconds")
    
    assert res.status_code == 200, f"Ingestion failed with status {res.status_code}"
    result = res.json()
    
    logger.info(f"Ingestion result: {result}")
    assert 'enriched' in result, "Ingestion result should indicate enrichment status"
    
    # Check if sentiment and topic were computed
    logger.info("Fetching enriched review data...")
    review_res = client.get('/reviews/1000', headers={'x-api-key':'supersecret'})
    assert review_res.status_code == 200, "Failed to fetch enriched review"
    
    review_data = review_res.json()
    logger.info(f"Enriched review data: {review_data}")
    
    # Verify AI enrichment worked (using fallback system)
    assert review_data['sentiment'] is not None, "Sentiment should be computed"
    assert review_data['topic'] is not None, "Topic should be computed"
    
    # Given the negative text and rating=1, sentiment should be negative
    # (This works even with fallback models)
    assert review_data['sentiment'].lower() in ['negative', 'neutral'], f"Expected negative sentiment for rating=1, got {review_data['sentiment']}"
    
    # Topic should be something reasonable (service, food, experience, etc.)
    assert len(review_data['topic']) > 0, "Topic should not be empty"
    
    logger.info(f"✅ AI enrichment test passed - Sentiment: {review_data['sentiment']}, Topic: {review_data['topic']}")
    logger.info("=== AI Enrichment Test Complete ===\n")


def test_ai_fallback_system():
    """Test that AI fallback system works correctly across different scenarios"""
    logger.info("=== Testing AI Fallback System Robustness ===")
    
    # Test different types of reviews to ensure fallback system handles variety
    test_scenarios = [
        {"id": 2001, "rating": 5, "text": "Excellent food and atmosphere!", "expected_sentiment": "positive"},
        {"id": 2002, "rating": 1, "text": "Worst meal ever, terrible service", "expected_sentiment": "negative"}, 
        {"id": 2003, "rating": 3, "text": "It was okay, nothing special", "expected_sentiment": "neutral"},
        {"id": 2004, "rating": 4, "text": "Good pizza but slow delivery", "expected_sentiment": "positive"},
    ]
    
    # Ingest test reviews
    reviews_data = []
    for scenario in test_scenarios:
        reviews_data.append({
            "id": scenario["id"],
            "location": "TestLocation",
            "rating": scenario["rating"], 
            "text": scenario["text"],
            "date": "2025-09-15"
        })
    
    logger.info(f"Ingesting {len(reviews_data)} test scenarios...")
    ingest_res = client.post('/ingest', json=reviews_data, headers={'x-api-key':'supersecret'}, params={'enrich': True})
    assert ingest_res.status_code == 200
    
    # Test AI reply generation for each scenario
    for scenario in test_scenarios:
        logger.info(f"Testing AI reply for scenario {scenario['id']}: '{scenario['text'][:30]}...'")
        
        reply_res = client.post(
            f"/reviews/{scenario['id']}/suggest-reply",
            json={},
            headers={'x-api-key':'supersecret'}
        )
        
        assert reply_res.status_code == 200, f"Reply generation failed for scenario {scenario['id']}"
        reply_data = reply_res.json()
        
        # Verify response structure
        assert 'reply' in reply_data
        assert 'reasoning_log' in reply_data
        assert len(reply_data['reply']) > 0, "Reply should not be empty"
        
        logger.info(f"✅ Scenario {scenario['id']} - Reply: '{reply_data['reply'][:40]}...', Reasoning: {reply_data['reasoning_log']}")
    
    logger.info("✅ AI fallback system test passed - All scenarios handled successfully")
    logger.info("=== AI Fallback System Test Complete ===\n")

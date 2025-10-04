from fastapi.testclient import TestClient
from app.main import app
import json
import logging
import time

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_ingest_and_list():
    """Test basic ingestion and listing functionality"""
    logger.info("=== Testing Basic Ingest and List ===")
    
    test_review = {
        "id": 100, 
        "location": "Test Location", 
        "rating": 4, 
        "text": "Nice restaurant with good food", 
        "date": "2025-09-10"
    }
    
    logger.info(f"Ingesting test review: {test_review}")
    
    # Test ingestion
    start_time = time.time()
    res = client.post('/ingest', json=[test_review], headers={'x-api-key':'supersecret'})
    ingest_time = time.time() - start_time
    
    logger.info(f"Ingestion completed in {ingest_time:.2f} seconds")
    logger.info(f"Ingestion response: {res.json()}")
    
    assert res.status_code == 200, f"Ingestion failed with status {res.status_code}"
    
    # Small delay to ensure database consistency
    time.sleep(0.1)
    
    # Test listing - use larger page size to ensure we get our test record
    logger.info("Fetching reviews list...")
    list_res = client.get('/reviews?page_size=100', headers={'x-api-key':'supersecret'})
    
    assert list_res.status_code == 200, f"List reviews failed with status {list_res.status_code}"
    
    reviews_data = list_res.json()
    logger.info(f"Found {len(reviews_data['reviews'])} reviews in database")
    
    # Debug: print all review IDs to see what's in the database
    review_ids = [r['id'] for r in reviews_data['reviews']]
    logger.info(f"Review IDs in database: {review_ids}")
    
    # Verify our review was ingested
    ingested_review = next((r for r in reviews_data['reviews'] if r['id'] == 100), None)
    assert ingested_review is not None, f"Ingested review ID 100 not found in list. Available IDs: {review_ids}"
    
    logger.info(f"Successfully found ingested review: ID={ingested_review['id']}, Rating={ingested_review['rating']}")
    
    # Verify review data integrity
    assert ingested_review['location'] == test_review['location']
    assert ingested_review['rating'] == test_review['rating']
    assert ingested_review['text'] == test_review['text']
    assert ingested_review['date'] == test_review['date']
    
    logger.info("✅ Basic ingest and list test passed")
    logger.info("=== Basic Ingest and List Test Complete ===\n")


def test_bulk_ingest():
    """Test bulk ingestion of multiple reviews"""
    logger.info("=== Testing Bulk Ingestion ===")
    
    bulk_reviews = [
        {"id": 201, "location": "NYC", "rating": 5, "text": "Excellent dining experience!", "date": "2025-09-01"},
        {"id": 202, "location": "Boston", "rating": 3, "text": "Average food, decent service", "date": "2025-09-02"},
        {"id": 203, "location": "Chicago", "rating": 2, "text": "Disappointing meal, slow service", "date": "2025-09-03"},
        {"id": 204, "location": "NYC", "rating": 4, "text": "Good ambience and tasty food", "date": "2025-09-04"},
        {"id": 205, "location": "Boston", "rating": 1, "text": "Terrible experience, would not recommend", "date": "2025-09-05"}
    ]
    
    logger.info(f"Ingesting {len(bulk_reviews)} reviews in bulk...")
    
    start_time = time.time()
    res = client.post('/ingest', json=bulk_reviews, headers={'x-api-key':'supersecret'}, params={'enrich': False})
    bulk_ingest_time = time.time() - start_time
    
    logger.info(f"Bulk ingestion completed in {bulk_ingest_time:.2f} seconds")
    logger.info(f"Bulk ingestion response: {res.json()}")
    
    assert res.status_code == 200, f"Bulk ingestion failed with status {res.status_code}"
    
    # Verify all reviews were ingested - use larger page size to ensure we get all test records
    logger.info("Verifying bulk ingested reviews...")
    list_res = client.get('/reviews?page_size=100', headers={'x-api-key':'supersecret'})
    assert list_res.status_code == 200
    
    all_reviews_data = list_res.json()
    ingested_ids = [r['id'] for r in all_reviews_data['reviews']]
    
    for review in bulk_reviews:
        assert review['id'] in ingested_ids, f"Review {review['id']} not found after bulk ingest"
    
    logger.info(f"✅ All {len(bulk_reviews)} reviews successfully ingested")
    
    # Test performance expectations
    expected_max_time = len(bulk_reviews) * 0.5  # Should be able to ingest at least 2 reviews per second
    assert bulk_ingest_time < expected_max_time, f"Bulk ingestion took too long: {bulk_ingest_time:.2f}s > {expected_max_time}s"
    
    logger.info(f"✅ Performance test passed - {len(bulk_reviews)} reviews in {bulk_ingest_time:.2f}s")
    logger.info("=== Bulk Ingestion Test Complete ===\n")


def test_ingest_with_enrichment_timing():
    """Test ingestion with AI enrichment and measure performance"""
    logger.info("=== Testing Ingest with AI Enrichment Timing ===")
    
    enrichment_review = {
        "id": 301,
        "location": "San Francisco", 
        "rating": 2,
        "text": "The pasta was overcooked and the service was incredibly slow. Very disappointing for the price.",
        "date": "2025-09-10"
    }
    
    logger.info(f"Ingesting review with AI enrichment: {enrichment_review}")
    
    # Test with enrichment enabled
    start_time = time.time()
    res = client.post('/ingest', json=[enrichment_review], headers={'x-api-key':'supersecret'}, params={'enrich': True})
    enrichment_time = time.time() - start_time
    
    logger.info(f"AI enrichment completed in {enrichment_time:.2f} seconds")
    
    assert res.status_code == 200, f"Enriched ingestion failed with status {res.status_code}"
    result = res.json()
    logger.info(f"Enrichment result: {result}")
    
    # Fetch the enriched review
    review_res = client.get('/reviews/301', headers={'x-api-key':'supersecret'})
    assert review_res.status_code == 200
    
    enriched_review = review_res.json()
    logger.info(f"Enriched review data: {enriched_review}")
    
    # Verify AI enrichment worked
    assert enriched_review['sentiment'] is not None, "Sentiment should be populated"
    assert enriched_review['topic'] is not None, "Topic should be populated"
    
    # Given the negative content, sentiment should be negative
    assert enriched_review['sentiment'].lower() in ['negative', 'neutral'], f"Expected negative sentiment, got {enriched_review['sentiment']}"
    
    # Performance check - enrichment should complete in reasonable time
    # (This accounts for model loading time on first run)
    max_expected_time = 120  # 2 minutes max for AI processing including model loading
    assert enrichment_time < max_expected_time, f"AI enrichment took too long: {enrichment_time:.2f}s > {max_expected_time}s"
    
    logger.info(f"✅ AI enrichment test passed - Sentiment: {enriched_review['sentiment']}, Topic: {enriched_review['topic']}")
    logger.info(f"✅ Performance: AI enrichment in {enrichment_time:.2f}s")
    logger.info("=== AI Enrichment Timing Test Complete ===\n")


def test_ingest_validation():
    """Test ingestion input validation and error handling"""
    logger.info("=== Testing Ingest Validation ===")
    
    # Test invalid API key
    logger.info("Testing invalid API key...")
    res = client.post('/ingest', json=[{"id": 401, "location": "Test", "rating": 4, "text": "Test", "date": "2025-09-10"}], headers={'x-api-key':'invalid'})
    logger.info(f"Invalid API key response: {res.status_code} - {res.json()}")
    assert res.status_code == 401, "Should reject invalid API key"
    
    # Test missing required fields
    logger.info("Testing missing required fields...")
    invalid_review = {"id": 402, "location": "Test"}  # Missing rating, text, date
    res = client.post('/ingest', json=[invalid_review], headers={'x-api-key':'supersecret'})
    logger.info(f"Missing fields response: {res.status_code} - {res.json()}")
    # Should reject with 400 (our validation) or other error codes
    assert res.status_code in [400, 422], f"Unexpected status code: {res.status_code}"
    
    # Test invalid JSON
    logger.info("Testing invalid JSON structure...")
    res = client.post('/ingest', data="invalid json", headers={'x-api-key':'supersecret', 'Content-Type': 'application/json'})
    logger.info(f"Invalid JSON response: {res.status_code}")
    assert res.status_code == 422, "Should reject invalid JSON"
    
    logger.info("✅ Input validation tests passed")
    logger.info("=== Ingest Validation Test Complete ===\n")

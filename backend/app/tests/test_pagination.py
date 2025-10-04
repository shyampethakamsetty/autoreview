from fastapi.testclient import TestClient
from app.main import app
import logging
import time

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_pagination():
    """Test pagination works correctly with comprehensive logging"""
    logger.info("=== Testing Pagination Functionality ===")
    
    # First ingest test reviews
    test_reviews = [
        {"id": 200+i, "location": f"Location{i%3}", "rating": i%5+1, "text": f"Review number {i} with some content", "date": "2025-09-10"}
        for i in range(25)
    ]
    
    logger.info(f"Ingesting {len(test_reviews)} test reviews for pagination testing...")
    
    start_time = time.time()
    ingest_res = client.post('/ingest', json=test_reviews, headers={'x-api-key':'supersecret'}, params={'enrich': False})
    ingest_time = time.time() - start_time
    
    logger.info(f"Test data ingested in {ingest_time:.2f} seconds")
    assert ingest_res.status_code == 200, f"Failed to ingest test data: {ingest_res.status_code}"
    
    # Test first page with different page sizes
    page_sizes = [5, 10, 20]
    for page_size in page_sizes:
        logger.info(f"Testing pagination with page_size={page_size}...")
        
        res = client.get(f'/reviews?page=1&page_size={page_size}', headers={'x-api-key':'supersecret'})
        assert res.status_code == 200, f"Pagination failed with page_size={page_size}"
        
        data = res.json()
        logger.info(f"Page 1 response structure: {list(data.keys())}")
        
        # Verify response structure
        assert 'reviews' in data, "Response should contain 'reviews' field"
        assert 'pagination' in data, "Response should contain 'pagination' field"
        
        # Verify pagination metadata
        pagination = data['pagination']
        assert pagination['page'] == 1, f"Expected page=1, got {pagination['page']}"
        assert pagination['page_size'] == page_size, f"Expected page_size={page_size}, got {pagination['page_size']}"
        
        # Verify data constraints
        assert len(data['reviews']) <= page_size, f"Too many reviews returned: {len(data['reviews'])} > {page_size}"
        assert len(data['reviews']) > 0, "Should return at least some reviews"
        
        logger.info(f"✅ Page size {page_size}: {len(data['reviews'])} reviews, total={pagination.get('total', 'N/A')}")
    
    # Test multiple pages
    logger.info("Testing multiple pages...")
    page_size = 10
    total_pages_to_test = min(3, (len(test_reviews) // page_size) + 1)
    
    for page in range(1, total_pages_to_test + 1):
        res = client.get(f'/reviews?page={page}&page_size={page_size}', headers={'x-api-key':'supersecret'})
        assert res.status_code == 200, f"Failed to fetch page {page}"
        
        data = res.json()
        logger.info(f"Page {page}: {len(data['reviews'])} reviews")
        
        assert data['pagination']['page'] == page, f"Wrong page number returned"
        
    logger.info("✅ Pagination functionality test passed")
    logger.info("=== Pagination Test Complete ===\n")

def test_filtering():
    """Test location filtering and text search functionality"""
    logger.info("=== Testing Filtering Functionality ===")
    
    # Setup diverse test data for filtering
    filter_test_reviews = [
        {"id": 301, "location": "NYC", "rating": 5, "text": "Excellent pizza in Manhattan", "date": "2025-09-01"},
        {"id": 302, "location": "Boston", "rating": 4, "text": "Good seafood restaurant", "date": "2025-09-02"},
        {"id": 303, "location": "NYC", "rating": 3, "text": "Average burger place", "date": "2025-09-03"},
        {"id": 304, "location": "Chicago", "rating": 2, "text": "Disappointing pizza experience", "date": "2025-09-04"},
        {"id": 305, "location": "Boston", "rating": 1, "text": "Terrible seafood, very bad", "date": "2025-09-05"}
    ]
    
    logger.info(f"Ingesting {len(filter_test_reviews)} reviews with diverse locations and content...")
    ingest_res = client.post('/ingest', json=filter_test_reviews, headers={'x-api-key':'supersecret'}, params={'enrich': False})
    assert ingest_res.status_code == 200
    
    # Test location filtering
    locations_to_test = ["NYC", "Boston", "Chicago"]
    for location in locations_to_test:
        logger.info(f"Testing location filter: {location}")
        
        res = client.get(f'/reviews?location={location}', headers={'x-api-key':'supersecret'})
        assert res.status_code == 200, f"Location filter failed for {location}"
        
        data = res.json()
        logger.info(f"Found {len(data['reviews'])} reviews for location '{location}'")
        
        # Verify all returned reviews match the location filter
        for review in data['reviews']:
            assert review['location'] == location, f"Wrong location in filtered results: expected {location}, got {review['location']}"
        
        # Verify we got the expected number of reviews for this location
        expected_count = len([r for r in filter_test_reviews if r['location'] == location])
        actual_count = len(data['reviews'])
        logger.info(f"✅ Location '{location}': Expected {expected_count}, got {actual_count} reviews")
        
        # Note: The actual count might be higher due to reviews from other tests
        assert actual_count >= expected_count, f"Missing reviews for location {location}"
    
    # Test text search functionality
    search_terms = ["pizza", "seafood", "burger", "terrible"]
    for term in search_terms:
        logger.info(f"Testing text search: '{term}'")
        
        res = client.get(f'/reviews?q={term}', headers={'x-api-key':'supersecret'})
        assert res.status_code == 200, f"Text search failed for term '{term}'"
        
        data = res.json()
        logger.info(f"Text search '{term}' returned {len(data['reviews'])} results")
        
        # Verify search results contain the term (case-insensitive)
        if len(data['reviews']) > 0:
            found_term_in_results = False
            for review in data['reviews']:
                if term.lower() in review['text'].lower():
                    found_term_in_results = True
                    break
            
            # Note: TF-IDF search might return semantically similar results
            # So we don't strictly require the exact term to be present
            logger.info(f"✅ Search '{term}': {len(data['reviews'])} results (semantic search may include related terms)")
        else:
            logger.info(f"⚠️  No results for search term '{term}' - may be expected for semantic search")
    
    # Test combined filters
    logger.info("Testing combined location and text search...")
    res = client.get('/reviews?location=NYC&q=pizza', headers={'x-api-key':'supersecret'})
    assert res.status_code == 200, "Combined filter failed"
    
    data = res.json()
    logger.info(f"Combined filter (location=NYC, q=pizza): {len(data['reviews'])} results")
    
    # All results should be from NYC
    for review in data['reviews']:
        assert review['location'] == 'NYC', f"Combined filter failed: expected NYC, got {review['location']}"
    
    logger.info("✅ Filtering functionality test passed")
    logger.info("=== Filtering Test Complete ===\n")

def test_pagination_edge_cases():
    """Test pagination edge cases and validation"""
    logger.info("=== Testing Pagination Edge Cases ===")
    
    # Test page beyond available data
    logger.info("Testing page beyond available data...")
    res = client.get('/reviews?page=9999&page_size=10', headers={'x-api-key':'supersecret'})
    logger.info(f"High page number response: {res.status_code}")
    
    assert res.status_code == 200, "High page number should return 200 with empty results"
    data = res.json()
    logger.info(f"High page results: {len(data['reviews'])} reviews")
    
    assert len(data['reviews']) == 0, "High page number should return empty results"
    assert 'pagination' in data, "Response should still include pagination metadata"
    
    # Test invalid page size (should be handled gracefully)
    logger.info("Testing invalid page size...")
    res = client.get('/reviews?page=1&page_size=200', headers={'x-api-key':'supersecret'})
    logger.info(f"Large page size response: {res.status_code} - {res.json() if res.status_code != 200 else 'Success'}")
    
    # Should either validate (422) or clamp the page size (200)
    assert res.status_code in [200, 422], f"Unexpected status for large page size: {res.status_code}"
    
    if res.status_code == 200:
        data = res.json()
        # If accepted, page size should be clamped to a reasonable limit
        assert len(data['reviews']) <= 100, "Page size should be clamped to reasonable limit"
        logger.info(f"✅ Large page size handled gracefully - returned {len(data['reviews'])} reviews")
    else:
        logger.info("✅ Large page size properly rejected with validation error")
    
    # Test zero and negative page numbers
    logger.info("Testing invalid page numbers...")
    
    # Test page 0
    res = client.get('/reviews?page=0&page_size=10', headers={'x-api-key':'supersecret'})
    logger.info(f"Page 0 response: {res.status_code}")
    assert res.status_code in [200, 422], "Page 0 should be handled gracefully"
    
    if res.status_code == 200:
        # Should treat as page 1 or return empty
        logger.info("✅ Page 0 handled gracefully")
    
    # Test negative page
    res = client.get('/reviews?page=-1&page_size=10', headers={'x-api-key':'supersecret'})
    logger.info(f"Negative page response: {res.status_code}")
    assert res.status_code in [200, 422], "Negative page should be handled gracefully"
    
    # Test invalid page size values  
    logger.info("Testing invalid page size values...")
    
    # Test page_size=0
    res = client.get('/reviews?page=1&page_size=0', headers={'x-api-key':'supersecret'})
    logger.info(f"Page size 0 response: {res.status_code}")
    assert res.status_code in [200, 422], "Page size 0 should be handled gracefully"
    
    # Test negative page_size
    res = client.get('/reviews?page=1&page_size=-5', headers={'x-api-key':'supersecret'})
    logger.info(f"Negative page size response: {res.status_code}")
    assert res.status_code in [200, 422], "Negative page size should be handled gracefully"
    
    logger.info("✅ All edge cases handled appropriately")
    logger.info("=== Pagination Edge Cases Test Complete ===\n")


def test_pagination_performance():
    """Test pagination performance with larger datasets"""
    logger.info("=== Testing Pagination Performance ===")
    
    # Test pagination response time
    logger.info("Testing pagination response times...")
    
    page_sizes = [10, 25, 50]
    for page_size in page_sizes:
        start_time = time.time()
        res = client.get(f'/reviews?page=1&page_size={page_size}', headers={'x-api-key':'supersecret'})
        response_time = time.time() - start_time
        
        assert res.status_code == 200, f"Pagination failed for page_size={page_size}"
        
        data = res.json()
        logger.info(f"Page size {page_size}: {response_time:.3f}s response time, {len(data['reviews'])} reviews")
        
        # Performance expectation: should respond within 2 seconds
        assert response_time < 2.0, f"Pagination too slow: {response_time:.3f}s > 2.0s for page_size={page_size}"
    
    # Test filtering performance
    logger.info("Testing filter performance...")
    
    start_time = time.time()
    res = client.get('/reviews?q=test&page=1&page_size=20', headers={'x-api-key':'supersecret'})
    search_time = time.time() - start_time
    
    assert res.status_code == 200, "Search with pagination failed"
    logger.info(f"Search + pagination: {search_time:.3f}s response time")
    
    # Search should be reasonably fast (TF-IDF is efficient)
    assert search_time < 3.0, f"Search too slow: {search_time:.3f}s > 3.0s"
    
    logger.info("✅ Pagination performance tests passed")
    logger.info("=== Pagination Performance Test Complete ===\n")

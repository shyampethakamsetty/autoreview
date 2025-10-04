from fastapi.testclient import TestClient
from app.main import app
import logging
import time

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_unauthorized():
    """Test unauthorized access to protected endpoints"""
    logger.info("=== Testing Unauthorized Access ===")
    
    # Test endpoints that require authentication
    get_endpoints = [
        '/reviews',
        '/analytics',  
        '/reviews/1'
    ]
    
    # Test GET endpoints (should return 401)
    for endpoint in get_endpoints:
        logger.info(f"Testing unauthorized access to GET {endpoint}")
        res = client.get(endpoint)
        logger.info(f"GET {endpoint}: {res.status_code} - {res.json()}")
        
        assert res.status_code == 401, f"Expected 401 for GET {endpoint}, got {res.status_code}"
        
        # Verify error response structure
        error_data = res.json()
        assert 'detail' in error_data, f"Error response should contain 'detail' field"
    
    # Test POST endpoints (may return 422 for validation before checking auth)
    post_endpoints = [
        ('/ingest', [{"id": 1, "location": "Test", "rating": 5, "text": "Test", "date": "2025-09-10"}]),
        ('/reviews/1/suggest-reply', {})
    ]
    
    for endpoint, data in post_endpoints:
        logger.info(f"Testing unauthorized access to POST {endpoint}")
        res = client.post(endpoint, json=data)
        logger.info(f"POST {endpoint}: {res.status_code} - {res.json()}")
        
        # Should return either 401 (auth checked first) or 422 (validation checked first)
        assert res.status_code in [401, 422], f"Expected 401 or 422 for POST {endpoint}, got {res.status_code}"
        
        # Verify error response structure
        error_data = res.json()
        assert 'detail' in error_data, f"Error response should contain 'detail' field"
        
    logger.info("✅ All unauthorized access properly blocked")
    logger.info("=== Unauthorized Access Test Complete ===\n")


def test_invalid_api_keys():
    """Test various invalid API key scenarios"""
    logger.info("=== Testing Invalid API Keys ===")
    
    invalid_keys = [
        'invalid',
        'wrong-key',
        '',
        'supersecre',  # typo
        'SUPERSECRET',  # wrong case
        'bearer supersecret',  # wrong format
        'null',
        '12345'
    ]
    
    for invalid_key in invalid_keys:
        logger.info(f"Testing invalid API key: '{invalid_key}'")
        
        res = client.get('/reviews', headers={'x-api-key': invalid_key})
        logger.info(f"Response: {res.status_code} - {res.json()}")
        
        assert res.status_code == 401, f"Invalid key '{invalid_key}' should be rejected"
        
        error_response = res.json()
        assert 'detail' in error_response, "Error response should have detail field"
        
    logger.info("✅ All invalid API keys properly rejected")
    logger.info("=== Invalid API Keys Test Complete ===\n")


def test_not_found_endpoints():
    """Test 404 responses for non-existent resources"""
    logger.info("=== Testing Not Found Scenarios ===")
    
    # Test non-existent review
    logger.info("Testing non-existent review access...")
    res = client.get('/reviews/99999', headers={'x-api-key': 'supersecret'})
    logger.info(f"Non-existent review response: {res.status_code} - {res.json()}")
    
    assert res.status_code == 404, f"Expected 404 for non-existent review, got {res.status_code}"
    
    # Test non-existent endpoints
    non_existent_endpoints = [
        '/nonexistent',
        '/reviews/invalid-id',
        '/api/nonexistent',
        '/wrong-path'
    ]
    
    for endpoint in non_existent_endpoints:
        logger.info(f"Testing non-existent endpoint: {endpoint}")
        res = client.get(endpoint, headers={'x-api-key': 'supersecret'})
        logger.info(f"{endpoint}: {res.status_code}")
        
        # Should return 404 for non-existent endpoints
        assert res.status_code == 404, f"Expected 404 for {endpoint}, got {res.status_code}"
    
    logger.info("✅ All not found scenarios handled correctly")
    logger.info("=== Not Found Test Complete ===\n")


def test_method_not_allowed():
    """Test unsupported HTTP methods on existing endpoints"""
    logger.info("=== Testing Method Not Allowed ===")
    
    # Test wrong methods on existing endpoints
    method_tests = [
        ('DELETE', '/reviews'),  # Should be GET
        ('PUT', '/reviews'),     # Should be GET  
        ('PATCH', '/reviews'),   # Should be GET
        ('GET', '/ingest'),      # Should be POST
        ('DELETE', '/ingest'),   # Should be POST
        ('PUT', '/analytics'),   # Should be GET
    ]
    
    for method, endpoint in method_tests:
        logger.info(f"Testing unsupported method {method} on {endpoint}")
        
        if method == 'DELETE':
            res = client.delete(endpoint, headers={'x-api-key': 'supersecret'})
        elif method == 'PUT':
            res = client.put(endpoint, headers={'x-api-key': 'supersecret'}, json={})
        elif method == 'PATCH':
            res = client.patch(endpoint, headers={'x-api-key': 'supersecret'}, json={})
        elif method == 'GET':
            res = client.get(endpoint, headers={'x-api-key': 'supersecret'})
            
        logger.info(f"{method} {endpoint}: {res.status_code}")
        
        # Should return 405 Method Not Allowed or 404 if route doesn't exist
        assert res.status_code in [404, 405], f"Expected 404/405 for {method} {endpoint}, got {res.status_code}"
    
    logger.info("✅ Unsupported methods properly handled")
    logger.info("=== Method Not Allowed Test Complete ===\n")


def test_malformed_requests():
    """Test handling of malformed request data"""
    logger.info("=== Testing Malformed Requests ===")
    
    # Test malformed JSON for ingest
    logger.info("Testing malformed JSON...")
    res = client.post('/ingest', 
                     data='{"invalid": json}',  # Invalid JSON
                     headers={'x-api-key': 'supersecret', 'Content-Type': 'application/json'})
    logger.info(f"Malformed JSON response: {res.status_code}")
    assert res.status_code == 422, "Malformed JSON should return 422"
    
    # Test wrong content type
    logger.info("Testing wrong content type...")
    res = client.post('/ingest',
                     data='some text data',
                     headers={'x-api-key': 'supersecret', 'Content-Type': 'text/plain'})
    logger.info(f"Wrong content type response: {res.status_code}")
    assert res.status_code in [422, 415], "Wrong content type should be rejected"
    
    # Test empty request body where data is expected
    logger.info("Testing empty request body...")
    res = client.post('/ingest', 
                     headers={'x-api-key': 'supersecret', 'Content-Type': 'application/json'})
    logger.info(f"Empty body response: {res.status_code}")
    assert res.status_code == 422, "Empty request body should return 422"
    
    # Test invalid query parameters
    logger.info("Testing invalid query parameters...")
    res = client.get('/reviews?page=invalid&page_size=also_invalid', 
                    headers={'x-api-key': 'supersecret'})
    logger.info(f"Invalid query params response: {res.status_code}")
    assert res.status_code == 422, "Invalid query parameters should return 422"
    
    logger.info("✅ All malformed requests properly handled")
    logger.info("=== Malformed Requests Test Complete ===\n")


def test_rate_limiting():
    """Test rate limiting functionality if implemented"""
    logger.info("=== Testing Rate Limiting (if implemented) ===")
    
    # Make rapid requests to test rate limiting
    request_count = 0
    rate_limited = False
    
    for i in range(20):  # Try 20 rapid requests
        res = client.get('/reviews?page=1&page_size=1', headers={'x-api-key': 'supersecret'})
        request_count += 1
        
        if res.status_code == 429:  # Too Many Requests
            logger.info(f"Rate limiting activated after {request_count} requests")
            rate_limited = True
            
            # Verify rate limit response
            error_data = res.json()
            assert 'detail' in error_data, "Rate limit response should have detail"
            logger.info(f"Rate limit message: {error_data['detail']}")
            break
        elif res.status_code != 200:
            logger.warning(f"Unexpected status during rate limit test: {res.status_code}")
    
    if rate_limited:
        logger.info("✅ Rate limiting is working")
        
        # Test that rate limit eventually clears
        logger.info("Waiting for rate limit to clear...")
        time.sleep(2)  # Wait a bit
        
        res = client.get('/reviews?page=1&page_size=1', headers={'x-api-key': 'supersecret'})
        if res.status_code == 200:
            logger.info("✅ Rate limit cleared after waiting")
        else:
            logger.info(f"Rate limit still active: {res.status_code}")
    else:
        logger.info("ℹ️  Rate limiting not implemented or threshold is higher than 20 requests")
    
    logger.info("=== Rate Limiting Test Complete ===\n")


def test_error_response_format():
    """Test that all error responses follow consistent format"""
    logger.info("=== Testing Error Response Format Consistency ===")
    
    # Collect various error responses
    error_scenarios = [
        (client.get('/reviews'), "No auth"),
        (client.get('/reviews', headers={'x-api-key': 'invalid'}), "Invalid auth"),
        (client.get('/reviews/99999', headers={'x-api-key': 'supersecret'}), "Not found"),
        (client.post('/ingest', data='invalid', headers={'x-api-key': 'supersecret', 'Content-Type': 'application/json'}), "Bad JSON"),
    ]
    
    for res, scenario in error_scenarios:
        logger.info(f"Testing error format for scenario: {scenario}")
        logger.info(f"Status: {res.status_code}, Response: {res.json()}")
        
        # All error responses should be JSON with detail field
        error_data = res.json()
        assert isinstance(error_data, dict), f"Error response should be JSON object for {scenario}"
        assert 'detail' in error_data, f"Error response should have 'detail' field for {scenario}"
        assert isinstance(error_data['detail'], str), f"Error detail should be string for {scenario}"
        assert len(error_data['detail']) > 0, f"Error detail should not be empty for {scenario}"
    
    logger.info("✅ All error responses follow consistent format")
    logger.info("=== Error Response Format Test Complete ===\n")

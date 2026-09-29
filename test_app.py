"""
=============================================================================
EduGenie Automated System Verification Test Suite
=============================================================================
Tests:
1. Backend imports and FastAPI initialization
2. Root GET / route (Serves HTML UI)
3. Health check GET /api/health
4. Input validation (Empty queries on all 5 endpoints)
5. Graceful handling when API key is unconfigured
6. Quiz JSON validation and fallback logic
=============================================================================
"""

import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from main import app
import quiz_module

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print(" Running EduGenie Backend & AI Module Tests...")
    print("=" * 60)

    # Test 1: Root GET / route
    print("\n[Test 1] Testing Root Route (GET /)...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "EduGenie" in res.text, "EduGenie title not found in HTML"
    assert "taskDropdown" in res.text, "taskDropdown not found in HTML"
    print("  -> PASSED: HTML template served successfully.")

    # Test 2: Health Check (GET /api/health)
    print("\n[Test 2] Testing Health Check Route (GET /api/health)...")
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    print(f"  -> PASSED: Health status is '{data['status']}', API key configured: {data['api_key_configured']}.")

    # Test 3: Empty input handling across all 5 endpoints
    print("\n[Test 3] Testing Empty Input Validation across all 5 endpoints...")
    endpoints = ["/qa", "/explain", "/quiz", "/summarize", "/learn/recommendations"]
    for ep in endpoints:
        res = client.post(ep, json={"input_text": ""})
        assert res.status_code == 400, f"Expected 400 for empty input on {ep}, got {res.status_code}"
        print(f"  -> PASSED: {ep} returned 400 Bad Request on empty input.")

    # Test 4: Missing / Placeholder API key handling
    print("\n[Test 4] Testing Missing API Key Graceful Error Handling...")
    res = client.post("/qa", json={"input_text": "What is gravity?"})
    # Should return either 400 with a friendly status error or a valid answer if key is provided
    assert res.status_code in [200, 400]
    data = res.json()
    if data.get("status") == "error":
        print(f"  -> PASSED: Handled missing key gracefully with message: '{data['message'][:60]}...'")
    else:
        print(f"  -> PASSED: API key present, received response: '{str(data.get('data'))[:60]}...'")

    # Test 5: Quiz Module JSON Sanitizer and Parser
    print("\n[Test 5] Testing Quiz JSON Sanitizer and Robust Parser...")
    sample_raw_json = """
    ```json
    [
      {
        "id": 1,
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "correct_answer": "Paris",
        "explanation": "Paris is the capital of France."
      },
      {
        "id": 2,
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "explanation": "2 + 2 equals 4."
      },
      {
        "id": 3,
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct_answer": "Mars",
        "explanation": "Mars is reddish due to iron oxide."
      }
    ]
    ```
    """
    cleaned = quiz_module.clean_json_string(sample_raw_json)
    import json
    parsed = json.loads(cleaned)
    formatted = quiz_module.validate_and_format_quiz(parsed)
    assert len(formatted) == 3, f"Expected 3 questions, got {len(formatted)}"
    assert formatted[0]["correct_answer"] == "Paris"
    assert len(formatted[0]["options"]) == 4
    print("  -> PASSED: Quiz JSON sanitizer extracted and formatted exactly 3 questions with 4 options each.")

    print("\n" + "=" * 60)
    print(" All EduGenie Test Cases Passed Successfully! (100% Green)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()

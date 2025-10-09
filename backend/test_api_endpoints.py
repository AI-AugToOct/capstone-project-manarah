"""Test script to verify all Manarah API endpoints."""
import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_root():
    """Test root health check endpoint."""
    print("\n🔍 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
    print("✅ Root endpoint working")


def test_upload_image():
    """Test image upload endpoint."""
    print("\n📤 Testing image upload...")
    
    # Create a small test image if it doesn't exist
    test_image = Path("child.jpg")
    
    with open(test_image, 'rb') as f:
        files = {'file': ('child.jpg', f, 'image/jpeg')}
        data = {
            'user_id': 'test_user',
            'caption': 'Test image upload'
        }
        response = requests.post(f"{BASE_URL}/api/v1/content/upload", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 202  # Accepted for async processing
    content_id = response.json()["content_id"]
    print(f"✅ Upload successful, content_id: {content_id}")
    
    return content_id


def test_status_endpoint(content_id: str):
    """Test status check endpoint."""
    print(f"\n🔄 Testing status endpoint for {content_id}...")
    
    max_attempts = 30
    for i in range(max_attempts):
        response = requests.get(
            f"{BASE_URL}/api/v1/content/{content_id}/status",
            params={"user_id": "test_user"}
        )
        
        print(f"Attempt {i+1}/{max_attempts} - Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        assert response.status_code == 200
        
        status = data.get("status")
        if status == "completed":
            print("✅ Processing completed!")
            return True
        elif status == "failed":
            print(f"❌ Processing failed: {data.get('error')}")
            return False
        elif status == "processing":
            print("⏳ Still processing...")
            time.sleep(3)
        else:
            print(f"⚠️ Unknown status: {status}")
            time.sleep(3)
    
    print("⚠️ Timeout waiting for completion")
    return False


def test_details_endpoint(content_id: str):
    """Test details retrieval endpoint."""
    print(f"\n📊 Testing details endpoint for {content_id}...")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/content/{content_id}/details",
        params={"user_id": "test_user"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Content Type: {data.get('content_type')}")
        print(f"Decision Action: {data.get('decision', {}).get('action')}")
        print(f"Combined Score: {data.get('decision', {}).get('combined_score'):.2f}")
        print(f"Reasoning: {data.get('decision', {}).get('reasoning')}")
        print("✅ Details retrieved successfully")
        return True
    else:
        print(f"❌ Failed to get details: {response.json()}")
        return False


def test_error_handling():
    """Test error handling."""
    print("\n🛡️ Testing error handling...")
    
    # Test 404 - Non-existent content
    response = requests.get(
        f"{BASE_URL}/api/v1/content/fake_id/status",
        params={"user_id": "test_user"}
    )
    print(f"404 Test - Status: {response.status_code}")
    assert response.status_code == 404
    print("✅ 404 handling works")
    
    # Test invalid file type
    data = {
        'user_id': 'test_user',
        'caption': 'Invalid file test'
    }
    files = {'file': ('test.txt', b'invalid content', 'text/plain')}
    response = requests.post(f"{BASE_URL}/api/v1/content/upload", files=files, data=data)
    print(f"Invalid file test - Status: {response.status_code}")
    assert response.status_code == 400
    print("✅ Invalid file type handling works")


def test_cors():
    """Test CORS headers."""
    print("\n🌐 Testing CORS headers...")
    
    response = requests.options(
        f"{BASE_URL}/api/v1/content/upload",
        headers={"Origin": "http://localhost:5173"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
    print(f"Access-Control-Allow-Methods: {response.headers.get('access-control-allow-methods')}")
    
    # CORS should allow the origin
    assert "access-control-allow-origin" in response.headers
    print("✅ CORS configured correctly")


def main():
    """Run all endpoint tests."""
    print("=" * 60)
    print("🚀 Manarah API Endpoint Tests")
    print("=" * 60)
    
    try:
        # Test basic endpoints
        test_root()
        test_cors()
        test_error_handling()
        
        # Test full workflow
        content_id = test_upload_image()
        
        if test_status_endpoint(content_id):
            test_details_endpoint(content_id)
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API. Is the server running on port 8000?")
        print("Run: python -m uvicorn src.main:app --reload --port 8000")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

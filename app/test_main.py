from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_read_root():
    """Test that the root endpoint works correctly"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Medical Image Analysis API"}

def test_api_docs():
    """Test that the API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() 
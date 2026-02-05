from fastapi.testclient import TestClient

def test_signup_success(client: TestClient):
    response = client.post(
        "/auth/signup",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_signup_duplicate_email(client: TestClient):
    # First signup
    client.post(
        "/auth/signup",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    # Duplicate signup
    response = client.post(
        "/auth/signup",
        data={
            "username": "testuser2",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400

def test_signin_success(client: TestClient):
    # Create user first
    client.post(
        "/auth/signup",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    # Signin
    response = client.post(
        "/auth/signin",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_get_current_user(client: TestClient):
    # Signup
    signup_res = client.post(
        "/auth/signup",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    token = signup_res.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/auth/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # assert data["email"] == "test@example.com" # Removed as schema doesn't have email
    assert data["username"] == "testuser"

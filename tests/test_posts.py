from fastapi.testclient import TestClient

def get_auth_token(client: TestClient, username="testuser", email="test@example.com"):
    client.post(
        "/auth/signup",
        data={
            "username": username,
            "email": email,
            "password": "password123"
        }
    )
    response = client.post(
        "/auth/signin",
        json={
            "email": email,
            "password": "password123"
        }
    )
    return response.json()["access_token"]

def create_community(client: TestClient, token: str):
    res = client.post(
        "/community/new",
        headers={"Authorization": f"Bearer {token}"},
        data={"community_name": "PostCommunity"},
        files={"community_header_image": ("f.jpg", b"c", "image/jpeg")}
    )
    return res.json()["id"]

def test_create_post(client: TestClient):
    token = get_auth_token(client)
    community_id = create_community(client, token)
    
    # Assuming post_body is a query param based on route signature
    response = client.post(
        f"/app/new/{community_id}?post_body=Hello World",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["post_body"] == "Hello World"

def test_get_posts(client: TestClient):
    token = get_auth_token(client)
    community_id = create_community(client, token)
    
    # Create post
    client.post(
        f"/app/new/{community_id}?post_body=Post 1",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    response = client.get(
        f"/app/{community_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["post_body"] == "Post 1"

def test_post_detail(client: TestClient):
    token = get_auth_token(client)
    community_id = create_community(client, token)
    
    # Create post
    create_res = client.post(
        f"/app/new/{community_id}?post_body=DetailPost",
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create_res.json()["id"]
    
    # Get detail
    response = client.get(
        f"/app/{community_id}/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["post_body"] == "DetailPost"
    assert data["id"] == post_id

def test_delete_post(client: TestClient):
    token = get_auth_token(client)
    community_id = create_community(client, token)
    
    # Create post
    create_res = client.post(
        f"/app/new/{community_id}?post_body=DeleteMe",
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create_res.json()["id"]
    
    # Delete
    response = client.delete(
        f"/app/{community_id}/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Verify deletion
    detail_res = client.get(
        f"/app/{community_id}/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert detail_res.status_code == 404

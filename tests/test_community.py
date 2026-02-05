from fastapi.testclient import TestClient

def get_auth_token(client: TestClient, username="testuser", email="test@example.com"):
    # Signup helper
    client.post(
        "/auth/signup",
        data={
            "username": username,
            "email": email,
            "password": "password123"
        }
    )
    # Signin to get token
    response = client.post(
        "/auth/signin",
        json={
            "email": email,
            "password": "password123"
        }
    )
    return response.json()["access_token"]

def test_create_community_success(client: TestClient):
    token = get_auth_token(client)
    
    response = client.post(
        "/community/new",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "community_name": "Test Community",
            "community_description": "A test community"
        },
        files={
            "community_header_image": ("filename.jpg", b"fakeimagecontent", "image/jpeg")
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["community_name"] == "Test Community"
    assert "id" in data

def test_list_communities(client: TestClient):
    token = get_auth_token(client)
    
    # Create a community first
    client.post(
        "/community/new",
        headers={"Authorization": f"Bearer {token}"},
        data={"community_name": "C1"},
        files={"community_header_image": ("f.jpg", b"c", "image/jpeg")}
    )
    
    response = client.get(
        "/community/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_join_community(client: TestClient):
    token = get_auth_token(client)
    
    # Create community
    create_res = client.post(
        "/community/new",
        headers={"Authorization": f"Bearer {token}"},
        data={"community_name": "Joinable"},
        files={"community_header_image": ("f.jpg", b"c", "image/jpeg")}
    )
    community_id = create_res.json()["id"]
    
    # User 2 joins
    token2 = get_auth_token(client, username="user2", email="user2@example.com")
    response = client.post(
        f"/community/join_community/{community_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 201
    
    # Check joined communities
    joined_res = client.get(
        "/community/joined_communities",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert joined_res.json()[0]["associated_community_id"] == community_id

def test_leave_community(client: TestClient):
    token = get_auth_token(client)
    
    # Create and join implicitly
    create_res = client.post(
        "/community/new",
        headers={"Authorization": f"Bearer {token}"},
        data={"community_name": "LeaveTest"},
        files={"community_header_image": ("f.jpg", b"c", "image/jpeg")}
    )
    community_id = create_res.json()["id"]
    
    # Leave
    response = client.delete(
        f"/community/leave/{community_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 202
    
    # Verify left
    joined_res = client.get(
        "/community/joined_communities",
        headers={"Authorization": f"Bearer {token}"}
    )
    # create_res makes us join, so after leaving, it should be empty for this community
    # Depending on test isolation, we might have other communities, so checking specific community absence
    joined_ids = [c["associated_community_id"] for c in joined_res.json()]
    assert community_id not in joined_ids

def test_delete_community(client: TestClient):
    token = get_auth_token(client)
    
    # Create
    create_res = client.post(
        "/community/new",
        headers={"Authorization": f"Bearer {token}"},
        data={"community_name": "DeleteTest"},
        files={"community_header_image": ("f.jpg", b"c", "image/jpeg")}
    )
    community_id = create_res.json()["id"]
    
    # Delete
    response = client.delete(
        f"/community/{community_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 202
    
    # Verify deletion
    list_res = client.get(
        "/community/",
        headers={"Authorization": f"Bearer {token}"}
    )
    ids = [c["id"] for c in list_res.json()]
    assert community_id not in ids

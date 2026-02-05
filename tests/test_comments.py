from fastapi.testclient import TestClient

def get_auth_token(client: TestClient, username="commentuser", email="comment@example.com"):
    client.post("/auth/signup", data={"username": username, "email": email, "password": "pwm"})
    res = client.post("/auth/signin", json={"email": email, "password": "pwm"})
    return res.json()["access_token"]

def setup_post(client: TestClient, token):
    # Create community
    c_res = client.post(
        "/community/new",
        headers={"Authorization": f"Bearer {token}"},
        data={"community_name": "CommentComm"},
        files={"community_header_image": ("f.jpg", b"c", "image/jpeg")}
    )
    community_id = c_res.json()["id"]
    
    # Create post
    p_res = client.post(
        f"/app/new/{community_id}?post_body=CommentOnThis",
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = p_res.json()["id"]
    
    return community_id, post_id

def test_create_comment(client: TestClient):
    token = get_auth_token(client)
    community_id, post_id = setup_post(client, token)
    
    response = client.post(
        f"/app/add_comment/{community_id}/{post_id}/new?comment_body=FirstComment",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["comment_body"] == "FirstComment"
    assert data["associated_post_id"] == post_id

def test_list_comments(client: TestClient):
    token = get_auth_token(client)
    community_id, post_id = setup_post(client, token)
    
    # Add comment
    client.post(
        f"/app/add_comment/{community_id}/{post_id}/new?comment_body=ListMe",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    response = client.get(
        f"/app/comments/{community_id}/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["comment_body"] == "ListMe"

def test_comment_detail(client: TestClient):
    token = get_auth_token(client)
    community_id, post_id = setup_post(client, token)
    
    # Create
    create_res = client.post(
        f"/app/add_comment/{community_id}/{post_id}/new?comment_body=Detail",
        headers={"Authorization": f"Bearer {token}"}
    )
    comment_id = create_res.json()["id"]
    
    # Get detail
    response = client.get(
        f"/app/comment/{community_id}/{post_id}/{comment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["comment_body"] == "Detail"

def test_update_comment(client: TestClient):
    token = get_auth_token(client)
    community_id, post_id = setup_post(client, token)
    
    # Create
    create_res = client.post(
        f"/app/add_comment/{community_id}/{post_id}/new?comment_body=OldBody",
        headers={"Authorization": f"Bearer {token}"}
    )
    comment_id = create_res.json()["id"]
    
    # Update
    response = client.patch(
        f"/app/comment/{community_id}/{post_id}/{comment_id}?comment_body=NewBody",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 202
    assert response.json()["comment_body"] == "NewBody"

def test_delete_comment(client: TestClient):
    token = get_auth_token(client)
    community_id, post_id = setup_post(client, token)
    
    # Create
    create_res = client.post(
        f"/app/add_comment/{community_id}/{post_id}/new?comment_body=DeleteMe",
        headers={"Authorization": f"Bearer {token}"}
    )
    comment_id = create_res.json()["id"]
    
    # Delete
    response = client.delete(
        f"/app/comment/{community_id}/{post_id}/{comment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Verify
    get_res = client.get(
        f"/app/comment/{community_id}/{post_id}/{comment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_res.status_code == 404

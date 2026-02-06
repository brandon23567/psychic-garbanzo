from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..database import get_db
from ..models.community_models import *
from ..models.community_post_models import *
from ..models.user_models import *
from ..schemas.community_posts_schemas import *
from ..crud.community_posts_crud import *
from ..utils.user_utils import *
from typing import List

router = APIRouter(
    prefix="/app",
    tags=["Community posts endpoint"]
)


@router.post("/new/{community_id}", status_code=status.HTTP_201_CREATED, response_model=DisplayCommunityPostSchema)
def upload_new_post_to_community_route(
    community_id: str,
    post_body: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return upload_new_post_to_community(
        db,
        user_id,
        community_id,
        post_body
    )
    
@router.get("/{community_id}", status_code=status.HTTP_200_OK, response_model=List[DisplayCommunityPostSchema])
def get_posts_inside_community_route(
    community_id: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return get_all_posts_inside_community(
        db, 
        user_id, 
        community_id
    )
    
@router.get("/{community_id}/{post_id}", status_code=status.HTTP_200_OK, response_model=DisplayCommunityPostSchema)
def community_post_detail_route(
    community_id: str,
    post_id: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return community_post_detail(db, community_id, user_id, post_id)

@router.delete("/{community_id}/{post_id}", status_code=status.HTTP_200_OK)
def delete_community_post_route(
    community_id: str,
    post_id: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return delete_community_post(db, user_id, post_id, community_id)


# ################################# routes for the comments functionality now begin here ############################################


@router.post("/add_comment/{community_id}/{post_id}/new", status_code=status.HTTP_201_CREATED, response_model=DisplayCommunityPostCommentSchema)
def upload_new_comment_route(
    community_id: str,
    post_id: str,
    comment_body: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return add_new_comment(db, user_id, post_id, community_id, comment_body)


@router.get("/comments/{community_id}/{post_id}", status_code=status.HTTP_200_OK, response_model=List[DisplayCommunityPostCommentSchema])
def get_all_post_comments_route(
    community_id: str,
    post_id: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return view_post_comments(db, user_id, community_id, post_id)

# this is for single comment detail (NB)
@router.get("/comment/{community_id}/{post_id}/{comment_id}", status_code=status.HTTP_200_OK, response_model=DisplayCommunityPostCommentSchema)
def get_comment_detail_route(
    community_id: str,
    post_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return view_comment_detail(db, user_id, post_id, comment_id, community_id)


@router.patch("/comment/{community_id}/{post_id}/{comment_id}", status_code=status.HTTP_202_ACCEPTED, response_model=DisplayCommunityPostCommentSchema)
def update_comment_route(
    community_id: str,
    post_id: str,
    comment_id: str,
    comment_body: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return update_comment(db, comment_id, user_id, post_id, community_id, comment_body)


@router.delete("/comment/{community_id}/{post_id}/{comment_id}", status_code=status.HTTP_200_OK)
def delete_user_comment_route(
    community_id: str,
    post_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return delete_user_comment(db, comment_id, user_id, post_id, community_id)
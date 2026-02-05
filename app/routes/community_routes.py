from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from ..models.community_models import *
from ..schemas.community_schemas import *
from ..crud.community_crud import *
from ..routes.user_routes import oauth2_scheme
from ..database import get_db
from ..utils.user_utils import *
from typing import List

router = APIRouter(
    prefix="/community",
    tags=["Community endpoints"]
)


@router.post("/new", status_code=status.HTTP_201_CREATED, response_model=DisplayCommunitySchema)
def create_new_community_route(
    db: Session = Depends(get_db),
    community_name: str = Form(..., description="name of the new community"),
    community_description: str = Form(None, description="description of community"),
    community_header_image: UploadFile = File(..., description="Header image of the community"),
    auth_token: str = Depends(oauth2_scheme)
):
    
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")

    return create_new_community(
        db=db,
        associated_user_id=user_id,
        community_name=community_name,
        community_description=community_description,
        community_header_image=community_header_image
    )
    

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[DisplayCommunitySchema])
def display_all_communities_route(
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme)
):
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to be here"
        )
    return display_all_communities(db=db)


@router.post("/join_community/{community_id}", status_code=status.HTTP_201_CREATED, response_model=DisplayUserJoinedCommunitiesSchema)
def join_new_community_route(
    community_id: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return join_community(
        db=db,
        community_id=community_id,
        user_id=user_id 
    )
    

@router.get("/joined_communities", status_code=status.HTTP_200_OK, response_model=List[DisplayUserJoinedCommunitiesSchema])
def get_all_user_joined_communities_route(
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return get_all_user_joined_communities(
        db=db,
        user_id=user_id
    )
    

@router.delete("/leave/{community_id}", status_code=status.HTTP_202_ACCEPTED)
def leave_community_route(
    community_id: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return leave_community(
        db=db,
        user_id=user_id,
        community_id=community_id
    )
    

@router.delete("/{community_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_community_route(
    community_id: str,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    return delete_a_community(
        db=db,
        user_id=user_id,
        community_id=community_id
    )
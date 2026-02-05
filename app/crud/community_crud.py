from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update, and_, or_
from fastapi import HTTPException, status, Depends, UploadFile, File, Form
from ..utils.community_utils import *
from ..models.user_models import *
from ..models.community_models import *

# when user creates community, they should be memeber numer 1
def create_new_community(
    db: Session,
    associated_user_id: str,
    community_name: str = Form(..., description="name of the new community"),
    community_description: str = Form(None, description="description of community"),
    community_header_image: UploadFile = File(..., description="Header image of the community")
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == associated_user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot perform this action, please signin"
        )
        
    community_header_image_url = ""
    if community_header_image is not None:
        community_header_image_url = upload_image_to_cloudinary(community_header_image)
        
    if community_description is None:
        community_description = ""
        
    try:
        new_community_instance = CommunityModel(
            associated_user_id=associated_user_id,
            community_name=community_name,
            community_description=community_description,
            community_header_image=community_header_image_url
        )
        
        db.add(new_community_instance)
        db.flush()
        
        # this is where the user needs to join
        
        user_joining_their_community = JoinCommunityModel(
            associated_user_id=associated_user_id,
            associated_community_id=new_community_instance.id
        )
        
        db.add(user_joining_their_community)
        
        db.commit()
        db.refresh(new_community_instance)
        
        return new_community_instance
    
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to create the new community: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to create new community")
    

def display_all_communities(
    db: Session
):
    try:
        communities = db.execute(select(CommunityModel)).scalars().all()
        
        if not communities:
            return {
                "communities": []
            }
            
        return communities
        
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to get communities: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to fetch communities")
    

def join_community(
    db: Session,
    community_id: str,
    user_id: str 
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot perform this action, please signin"
        )
        
    valid_community = db.execute(select(CommunityModel).where(CommunityModel.id == community_id)).scalar_one_or_none()
    if not valid_community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid community, it does not exist"
        )
        
    try:
        user_joined_community_instance = JoinCommunityModel(
            associated_user_id=user_id,
            associated_community_id=community_id
        )
        
        db.add(user_joined_community_instance)
        db.commit()
        db.refresh(user_joined_community_instance)
        
        return user_joined_community_instance
        
    except Exception as e:
        db.rollback()
        print(f"Unable to join this community: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to join community")
    

def get_all_user_joined_communities(
    db: Session,
    user_id: str 
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot perform this action, please signin"
        )
        
    try:
        users_joined_communities = db.execute(select(JoinCommunityModel).where(
            JoinCommunityModel.associated_user_id == user_id    
        )).scalars().all()
        
        if not users_joined_communities:
            return{
                "communities": []
            }
            
        return users_joined_communities
        
    except Exception as e:
        db.rollback()
        print(f"There was an issue trying to get users joined communities: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to get your joined communities")
    


# currently we will delete but in a real system or for v2 we might just want to mark it as left or something like that
def leave_community(
    db: Session,
    user_id: str,
    community_id: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot perform this action, please signin"
        )
        
    valid_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not valid_community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not part of this community for you to leave it"
        )
        
    try:
        db.delete(valid_community)
        db.commit()
        
        return {
            "message": "You have left the community"
        }
        
    except Exception as e:
        db.rollback()
        print(f"Unable to leave the community: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to leave the community")
    

def delete_a_community(
    db: Session,
    user_id: str,
    community_id: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot perform this action, please signin"
        )
        
    valid_community = db.execute(select(CommunityModel).where(
        and_(
            CommunityModel.id == community_id,
            CommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not valid_community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You cannot delete what you did not create bruh, lock in"
        )
        
    try:
        db.delete(valid_community)
        db.commit()
        
        return {
            "message": "Community has been deleted"
        }
        
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to delete the community: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to delete the community")
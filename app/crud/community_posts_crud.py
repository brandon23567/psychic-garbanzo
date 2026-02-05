from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, delete, update
from ..models.community_post_models import *
from ..models.user_models import *
from ..models.community_models import *
from ..schemas.community_posts_schemas import *
from fastapi import HTTPException, UploadFile, Form, File, Depends, status


def upload_new_post_to_community(
    db: Session,
    user_id: str,
    community_id: str,
    post_body: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
        
    is_joined_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not is_joined_community:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not joined this community so you can make posts to it"
        )
        
    try:
        new_post = CommunityPostModel(
            associated_user_id=user_id,
            associated_community_id=community_id,
            post_body=post_body
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        
        return new_post
        
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to upload the new post to the community: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to upload the new post"
        )
        

def get_all_posts_inside_community(
    db: Session,
    user_id: str,
    community_id: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
        
    is_joined_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not is_joined_community:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not joined this community so you can make posts to it"
        )
    
    try:
        community_posts = db.execute(select(CommunityPostModel).where(
            CommunityPostModel.associated_community_id == community_id
        )).scalars().all()
        
        return community_posts
    
    except Exception as e:
        db.rollback()
        
        print(f"There was an error trying to get posts of community: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch posts at this current moment"
        )
        

def community_post_detail(
    db: Session,
    community_id: str,
    user_id: str,
    post_id: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
        
    is_joined_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not is_joined_community:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not joined this community so you can make posts to it"
        )
        
    try:
        community_post = db.execute(select(CommunityPostModel).where(
            and_(
                CommunityPostModel.associated_community_id == community_id,
                CommunityPostModel.associated_user_id == user_id,
                CommunityPostModel.id == post_id
            )
        )).scalar_one_or_none()
        
        if not community_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found. Maybe it has been deleted. Sorry"
            )
            
        return community_post
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"There was an error trying to get the post detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to get post detail"
        )
        

def delete_community_post(
    db: Session,
    user_id: str,
    post_id: str,
    community_id: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
        
    is_joined_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not is_joined_community:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not joined this community so you can make posts to it"
        )
        
    try:
        post_to_delete = db.execute(select(CommunityPostModel).where(
            and_(
                CommunityPostModel.id == post_id,
                CommunityPostModel.associated_user_id == user_id,
                CommunityPostModel.associated_community_id == community_id
            )
        )).scalar_one_or_none()
        
        if not post_to_delete:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to delete this for you"
            )
            
        db.delete(post_to_delete)
        db.commit()
        
        return {
            "message": "post has been deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"There was an issue trying to delete the post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete post"
        )
        
# ########################################## now the functionality for the comments section type shii #########################


def add_new_comment(
    db: Session,
    user_id: str,
    post_id: str,
    community_id: str,
    comment_body: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
        
    is_joined_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not is_joined_community:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not joined this community so you can make posts to it"
        )
        
    try:
        new_comment_instance = CommunityPostCommentModel(
            associated_user_id=user_id,
            associated_community_id=community_id,
            associated_post_id=post_id,
            comment_body=comment_body
        )
        
        db.add(new_comment_instance)
        db.commit()
        db.refresh(new_comment_instance)
        
        return new_comment_instance
        
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to add new comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to upload the comment"
        )
        

def view_post_comments(
    db: Session,
    user_id: str,
    community_id: str,
    post_id: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
        
    is_joined_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not is_joined_community:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not joined this community so you can make posts to it"
        )
        
    try:
        post_comments = db.execute(select(CommunityPostCommentModel).where(
            and_(
                CommunityPostCommentModel.associated_community_id == community_id,
                CommunityPostCommentModel.associated_post_id == post_id
            )
        )).scalars().all()
        
        return post_comments
        
    except Exception as e:
        print(f"There was an error trying to view comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch the comments right now"
        )
        

def view_comment_detail(
    db: Session, 
    user_id: str,
    post_id: str,
    comment_id: str,
    community_id: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
        
    is_joined_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not is_joined_community:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not joined this community so you can make posts to it"
        )
        
    try:
        comment_instance = db.execute(select(CommunityPostCommentModel).where(
            and_(
                CommunityPostCommentModel.id == comment_id,
                CommunityPostCommentModel.associated_community_id == community_id,
                CommunityPostCommentModel.associated_post_id == post_id
            )
        )).scalar_one_or_none()
        
        if not comment_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found"
            )
            
        return comment_instance
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unable to get details of comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to get comment details"
        )
        

def update_comment(
    db: Session,
    comment_id: str,
    user_id: str,
    post_id: str,
    community_id: str, 
    comment_body: str
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
        
    is_joined_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not is_joined_community:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not joined this community so you can make posts to it"
        )
        
    try:
        comment_instance = db.execute(select(CommunityPostCommentModel).where(
            and_(
                CommunityPostCommentModel.id == comment_id,
                CommunityPostCommentModel.associated_user_id == user_id,
                CommunityPostCommentModel.associated_community_id == community_id,
                CommunityPostCommentModel.associated_post_id == post_id
            )
        )).scalar_one_or_none()
        
        if not comment_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found"
            )
            
        comment_instance.comment_body = comment_body
        db.commit()
        db.refresh(comment_instance)
        
        return comment_instance
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Unable to update the comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update comment"
        )
        

def delete_user_comment(
    db: Session,
    comment_id: str,
    user_id: str,
    post_id: str,
    community_id: str, 
):
    existing_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
        
    is_joined_community = db.execute(select(JoinCommunityModel).where(
        and_(
            JoinCommunityModel.associated_community_id == community_id,
            JoinCommunityModel.associated_user_id == user_id
        )
    )).scalar_one_or_none()
    
    if not is_joined_community:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not joined this community so you can make posts to it"
        )
        
    try:
        comment_instance = db.execute(select(CommunityPostCommentModel).where(
            and_(
                CommunityPostCommentModel.id == comment_id,
                CommunityPostCommentModel.associated_user_id == user_id,
                CommunityPostCommentModel.associated_community_id == community_id,
                CommunityPostCommentModel.associated_post_id == post_id
            )
        )).scalar_one_or_none()
        
        if not comment_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found"
            )
            
        db.delete(comment_instance)
        db.commit()
        
        return {
            "message": "Comment has been deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Unable to delete the comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete comment"
        )
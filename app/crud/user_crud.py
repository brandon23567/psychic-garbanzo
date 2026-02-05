from ..database import Base, get_db
from ..models.user_models import *
from ..schemas.user_schemas import *
from sqlalchemy import select, delete, update 
from sqlalchemy.orm import Session
import bcrypt
from fastapi import HTTPException, File, UploadFile, Depends, status, Form
from ..utils.user_utils import *

# USER_PROFILE_IMAGES_DIR = "user_profile_images"

def signup_new_user(
    db: Session,
    username: str = Form(..., description="username"),
    email: str = Form(..., description="user email"),
    password: str = Form(..., description="user password"),
    user_profile_image: UploadFile = File(None, description="users profile image if provided")
):
    
    existing_user = db.execute(select(UserModel).where(UserModel.email == email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already have an account, please log in"
        )
        
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password, salt)
    
    new_user_profile_image_url = ""
    
    if user_profile_image is not None:
        new_user_profile_image_url = upload_image_to_cloudinary(file=user_profile_image)
    
    try:
        new_user_instance = UserModel(
            username=username,
            email=email,
            password=hashed_password,
            user_profile_image=new_user_profile_image_url
        )
        
        db.add()
        db.refresh(new_user_instance)
        
        user_token_data = {
            "sub": new_user_instance.id,
            "username": new_user_instance.username
        }
        
        user_tokens = generate_user_tokens(user_token_data)
            
        return user_tokens
        
    except Exception as e:
        print(f"There was an error trying to signup the new user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to signup the user"
        )
        

def signin_user(
    db: Session,
    user_data: UserSigninSchema
):
    existing_user = db.execute(select(UserModel).where(UserModel.email == user_data.email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already have an account, please log in"
        )
        
    try:
        check_password = bcrypt.checkpw(user_data.password, existing_user.password)
        if not check_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials used for login"
            )
            
        user_token_data = {
            "sub": existing_user.id,
            "username": existing_user.username
        }
        
        user_tokens = generate_user_tokens(user_token_data)
            
        return user_tokens
        
    except Exception as e:
        print(f"There was an error trying to signin the user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to signin to your account"
        )
        
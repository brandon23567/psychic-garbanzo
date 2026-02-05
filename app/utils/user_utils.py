import os 
import cloudinary
import cloudinary.api
from dotenv import load_dotenv
from fastapi import HTTPException, status, File, Form, UploadFile
import json 
from datetime import datetime, timedelta, timezone
import jwt

load_dotenv()

CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXIRE_DAYS = 7

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET
)

def upload_image_to_cloudinary(
    file: UploadFile = File(..., description="The file to be uploaded to cloudinary")
):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            use_filename=True,
            unique_filename=True,
            folder="user_profile_images"
        )
        
        user_image_link = result["secure_url"]
        
        return user_image_link
        
    except Exception as e:
        print(f"There was an error trying to upload the file: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to upload the requested file")
    
    
    
def generate_access_token(user_data: dict) -> str:
    try:
        access_token_data = user_data.copy()
        expires_in = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token_data.update({ "exp": expires_in, "type": "access" })
        access_token = jwt.encode(access_token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        return access_token
        
    except Exception as e:
        print(f"Unable to generate the users access token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to generate the access token")    


def generate_refresh_token(user_data: dict) -> str:
    try:
        refresh_token_data = user_data.copy()
        expires_in = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXIRE_DAYS)
        refresh_token_data.update({ "exp": expires_in, "type": "refresh" })
        refresh_token = jwt.encode(refresh_token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        return refresh_token
        
    except Exception as e:
        print(f"Unable to generate the users refresh token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to generate the refresh token")   


def generate_user_tokens(user_data: dict) -> dict:
    try:
        access_token = generate_access_token(user_data)
        refresh_token = generate_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        
    except Exception as e:
        print(f"There was an error trying to generate the users tokens: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to get tokens")
    


def decode_access_token(access_token: str) -> dict:
    try:
        decoded_token = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to decode the provided token"
            )
            
        return decoded_token
    
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid token signature"
        )
        
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
    except Exception as e:
        print(f"There was an error trying to decode the token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to verify this token")


def refresh_user_token(refresh_token: str) -> dict:
    try:
        decoded_token = decode_access_token(refresh_token)
        
        if decoded_token.type != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type passed")
        
        user_id = decoded_token.get("sub")
        username = decoded_token.get("username")
        
        new_token_data = {
            "sub": user_id,
            "username": username
        }
        
        user_tokens = generate_user_tokens(new_token_data)
        
        return user_tokens
        
    except Exception as e:
        print(f"There was an error trying to refresh the user token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to refresh token")
    

def get_current_user(access_token: str) -> dict:
    try:
        decoded_token = decode_access_token(access_token)
        
        username = decoded_token.get("username")
        user_id = decoded_token.get("user_id")
        
        return{
            "username": username,
            "user_id": user_id
        }
        
    except Exception as e:
        print(f"There was an error trying to get the current user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
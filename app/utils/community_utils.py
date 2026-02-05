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

cloudinary.config(
    cloud_name = "",
    api_key = "",
    api_secret = ""
)

def upload_image_to_cloudinary(
    file: UploadFile = File(..., description="The file to be uploaded to cloudinary")
):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            use_filename=True,
            unique_filename=True,
            folder="community_header_images"
        )
        
        user_image_link = result["secure_url"]
        
        return {
            "message": "Image was uploaded",
            "image_url": user_image_link
        }
        
    except Exception as e:
        print(f"There was an error trying to upload the file: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to upload the requested file")
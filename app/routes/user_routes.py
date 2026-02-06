from fastapi import APIRouter, HTTPException, status, File, Form, UploadFile, Depends, Response, Request
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.security import APIKeyCookie
from ..crud.user_crud import (
    signup_new_user, signin_user, get_user_by_id
)
from ..utils.user_utils import (
    decode_access_token, refresh_user_token, get_token_from_cookie, 
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXIRE_DAYS
)
from ..schemas.user_schemas import *
from typing import Optional
import os

IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"

# New dependency to get token from cookie
def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication endpoints"]
)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup_new_user_route(
    response: Response,
    db: Session = Depends(get_db),
    username: str = Form(..., description="username"),
    email: str = Form(..., description="user email"),
    password: str = Form(..., description="user password"),
    user_profile_image: UploadFile = File(None, description="users profile image if provided")
):
    user_tokens = signup_new_user(
        db=db,
        username=username,
        email=email,
        password=password,
        user_profile_image=user_profile_image
    )
    
    # Set cookies
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=user_tokens["access_token"],
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=IS_PRODUCTION 
    )
    
    response.set_cookie(
        key="refresh_token",
        value=user_tokens["refresh_token"],
        httponly=True,
        max_age=REFRESH_TOKEN_EXIRE_DAYS * 24 * 60 * 60,
        expires=REFRESH_TOKEN_EXIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=IS_PRODUCTION 
    )
    
    return {"message": "Successfully signed up and logged in"}
    

@router.post("/signin", status_code=status.HTTP_200_OK)
def signin_user_route(
    response: Response,
    user_data: UserSigninSchema,
    db: Session = Depends(get_db),
):
    user_tokens = signin_user(
        db=db,
        user_data=user_data
    )
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=user_tokens["access_token"],
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=IS_PRODUCTION
    )
    
    response.set_cookie(
        key="refresh_token",
        value=user_tokens["refresh_token"],
        httponly=True,
        max_age=REFRESH_TOKEN_EXIRE_DAYS * 24 * 60 * 60,
        expires=REFRESH_TOKEN_EXIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=IS_PRODUCTION
    )
    
    return {"message": "Successfully signed in"}

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user_route(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out"}


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_token_route(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )
        
    try:
        new_tokens = refresh_user_token(refresh_token)
        
        # Set cookies
        response.set_cookie(
            key="access_token",
            value=new_tokens["access_token"],
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
            expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=IS_PRODUCTION
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_tokens["refresh_token"],
            httponly=True,
            max_age=REFRESH_TOKEN_EXIRE_DAYS * 24 * 60 * 60,
            expires=REFRESH_TOKEN_EXIRE_DAYS * 24 * 60 * 60,
            samesite="lax",
            secure=IS_PRODUCTION
        )
        
        return {"message": "Token refreshed"}
        
    except Exception as e:
        # Clear cookies if refresh fails
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    

@router.get("/", status_code=status.HTTP_200_OK, response_model=DisplayUserSchema)
def get_current_user_route(
    db: Session = Depends(get_db),
    auth_token: str = Depends(get_token_from_cookie)
):
    decoded_token = decode_access_token(auth_token)
    user_id = decoded_token.get("sub")
    
    current_user = get_user_by_id(db, user_id)
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return current_user
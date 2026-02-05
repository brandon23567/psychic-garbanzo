from fastapi import APIRouter, HTTPException, status, File, Form, UploadFile, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.security.oauth2 import OAuth2PasswordBearer
from ..crud.user_crud import *
from ..schemas.user_schemas import *
from ..utils.user_utils import *

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication endpoints"]
)

@router.post("/signin", status_code=status.HTTP_201_CREATED, response_model=DisplayUserSchema)
def signup_new_user_route(
    db: Session = Depends(get_db),
    username: str = Form(..., description="username"),
    email: str = Form(..., description="user email"),
    password: str = Form(..., description="user password"),
    user_profile_image: UploadFile = File(None, description="users profile image if provided")
):
    return signup_new_user(
        db=db,
        username=username,
        email=email,
        password=password,
        user_profile_image=user_profile_image
    )
    

@router.post("/signin", status_code=status.HTTP_200_OK, response_model=DisplayUserSchema)
def signin_user_route(
    db: Session,
    user_data: UserSigninSchema
):
    return signin_user(
        db=db,
        user_data=user_data
    )
    

@router.get("/", status_code=status.HTTP_200_OK, response_model=DisplayUserSchema)
def get_current_user_route(
    auth_token: str = Depends(oauth2_scheme)
):
    return get_current_user(auth_token)
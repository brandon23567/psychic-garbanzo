from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class CreateUserSchema(BaseModel):
    username: str = Field(..., description="users username")
    email: EmailStr = Field(..., description="users email")
    user_profile_image: Optional[str] = Field(None, description="profile image if provided")
    password: str = Field(..., description="user password")
    
    class Config:
        from_attributes = True 
  
class UserSigninSchema(BaseModel):
    email: EmailStr = Field(..., description="users email to signin")
    password: str = Field(..., description="users password to signin")
    
    class Config:
        from_attributes = True      
        
class DisplayUserSchema(BaseModel):
    id: str 
    username: str 
    user_profile_image: Optional[str]
    date_created: datetime
    
    class Config:
        from_attributes = True 
        
        
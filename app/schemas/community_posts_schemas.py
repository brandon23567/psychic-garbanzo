from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CreateCommunityPostSchema(BaseModel):
    associated_community_id: str = Field(..., description="id of the community to post to")
    post_body: str = Field(..., description="Actual body of the post we are making")
    
    model_config = ConfigDict(from_attributes=True)
        

class DisplayCommunityPostSchema(BaseModel):
    id: str 
    associated_community_id: str 
    post_body: str 
    date_posted: datetime
    
    model_config = ConfigDict(from_attributes=True)
        

class CreateCommunityPostCommentSchema(BaseModel):
    associated_community_id: str = Field(..., description="community to post to")
    associated_post_id: str = Field(..., description="id of the post we are commenting on")
    comment_body: str = Field(..., description="Actual comment body")
    
    model_config = ConfigDict(from_attributes=True)
        

class DisplayCommunityPostCommentSchema(BaseModel):
    id: str 
    associated_user_id: str
    associated_community_id: str 
    associated_post_id: str 
    comment_body: str 
    
    model_config = ConfigDict(from_attributes=True)
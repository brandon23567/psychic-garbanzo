from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class DisplayCommunitySchema(BaseModel):
    id: str 
    associated_user_id: str
    community_name: str 
    community_description: Optional[str]
    community_header_image: str 
    date_created: datetime
    
    model_config = ConfigDict(from_attributes=True)
        

class JoinCommunitySchema(BaseModel):
    associated_user_id: str = Field(..., description="id of the user joining")
    associated_community_id: str = Field(..., description="id of the community being joined")
    
    model_config = ConfigDict(from_attributes=True)
        

class DisplayUserJoinedCommunitiesSchema(BaseModel):
    id: str
    associated_user_id: str 
    associated_community_id: str 
    date_joined: datetime
    
    model_config = ConfigDict(from_attributes=True)
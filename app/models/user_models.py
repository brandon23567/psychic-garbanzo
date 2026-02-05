from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4 
from ..database import Base 


class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    user_profile_image = Column(String, nullable=True)
    password = Column(String, nullable=False)
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    communities = relationship("CommunityModel", back_populates="user")
    joined_communities = relationship("JoinCommunityModel", back_populates="user")
    posts = relationship("CommunityPostModel", back_populates="user")
    post_comments = relationship("CommunityPostCommentModel", back_populates="user")
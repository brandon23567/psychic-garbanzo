from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4 
from ..database import Base 


class CommunityPostModel(Base):
    __tablename__ = "posts"
    
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    associated_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    associated_community_id = Column(String, ForeignKey("communities.id"), nullable=False)
    post_body = Column(Text, nullable=False)
    date_posted = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("UserModel", back_populates="posts")
    community = relationship("CommunityModel", back_populates="posts")
    post_comments = relationship("CommunityPostCommentModel", back_populates="community_post")
    
    
class CommunityPostCommentModel(Base):
    __tablename__ = "post_comments"
    
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    associated_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    associated_community_id = Column(String, ForeignKey("communities.id"), nullable=False)
    associated_post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    comment_body = Column(Text, nullable=False)
    date_posted = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("UserModel", back_populates="post_comments")
    community_post = relationship("CommunityPostModel", back_populates="post_comments")
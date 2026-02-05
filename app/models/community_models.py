from sqlalchemy import Column, Text, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4
from ..database import Base


class CommunityModel(Base):
    __tablename__ = "communities"
    
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    associated_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    community_name = Column(String, nullable=False)
    community_description = Column(Text, nullable=True)
    community_header_image = Column(String, nullable=False)
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("UserModel", back_populates="communities")
    posts = relationship("CommunityPostModel", back_populates="community")
    

class JoinCommunityModel(Base):
    __tablename__ = "joined_communitites"
    
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    associated_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    associated_community_id = Column(String, ForeignKey("communities.id"), nullable=False)
    date_joined = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("UserModel", back_populates="joined_communities")
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
# Import models to ensure they are registered with Base
from app.models.user_models import UserModel
from app.models.community_models import CommunityModel
from app.models.community_post_models import CommunityPostModel, CommunityPostCommentModel

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a fresh database session for a test.
    recreates tables for each test to ensure isolation.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI TestClient with overridden database dependency.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_cloudinary(monkeypatch):
    mock_upload = MagicMock(return_value={"secure_url": "http://mocked.url/image.jpg"})
    monkeypatch.setattr("cloudinary.uploader.upload", mock_upload)

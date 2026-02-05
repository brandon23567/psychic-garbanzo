from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.user_routes import router as auth_routes
from .routes.community_routes import router as community_routes
from .routes.community_posts_routes import router as community_posts_routes

app = FastAPI(
    title="Community Platform",
    description="New platform for users to create their communities to manage",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

app.include_router(auth_routes)
app.include_router(community_routes)
app.include_router(community_posts_routes)

@app.get("/")
def home_root():
    return { "message": "Hello there manual code once more" }
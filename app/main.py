from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base

from app.routers import users
from app.routers import auth_routes
from app.routers import categories

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth_routes.router)
app.include_router(categories.router)


@app.get("/")
def home():
    return {
        "message": "Finance Tracker API Running"
    }
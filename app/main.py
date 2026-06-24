from urllib import request

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine
from .database import get_db

from .models import Base
from .models import User

from .schemas import UserCreate, UserUpdate
from .schemas import UserResponse
from .security import hash_password
from .schemas import LoginRequest
from .security import verify_password
import app.models as models 
from .auth import create_access_token
from .schemas import Token
from fastapi import Header
from .auth import verify_token

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Finance Tracker API Running"
    }

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.post("/users",response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    db_user = User(
        username=user.username,
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    
    existing_username = db.query(User).filter(
        User.username == user.username
    ).first()
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_username:
        raise HTTPException(
        status_code=400,
        detail="Username already taken"
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updated_user: UserUpdate,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.name = updated_user.name
    user.email = updated_user.email

    db.commit()
    db.refresh(user)

    return user

@app.post("/login", response_model=Token)
def login(user: LoginRequest, db: Session = Depends(get_db)):

    db_user = (
        db.query(models.User).filter(
            (User.email == user.username_or_email) |
            (User.username == user.username_or_email)
        ).first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email/username or password"
        )

    if not verify_password(
        user.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email/username or password"
        )

    access_token = create_access_token(
    {
        "sub": str(db_user.id)
    }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/dashboard")
def dashboard(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Token missing"
        )

    token = authorization.replace(
        "Bearer ",
        ""
    )

    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    return {
        "message": "Welcome",
        "username": user.username,
        "name": user.name,
        "email": user.email
    }
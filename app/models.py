from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from database import Base

# --- DATABASE MODELS (SQLAlchemy) ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)


# --- REQUEST SCHEMAS (Pydantic) ---

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class UserCreateModel(BaseModel):
    username: str = Field(max_length=20)
    email: str = Field(max_length=50)
    password: str = Field(min_length=8)
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)


class UserModel(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserLoginModel(BaseModel):
    email: str = Field(max_length=50)
    password: str

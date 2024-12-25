from pydantic import BaseModel, Field


class UserCreateModel(BaseModel):
    username: str = Field(max_length=10)
    email: str = Field(max_length=50)
    password: str = Field(min_length=8)

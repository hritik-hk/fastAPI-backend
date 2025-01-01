from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
import uuid


# defining models for input validations using pydantic
class Book(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    publisher: str
    publish_date: date
    page_count: int
    language: str
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    publish_date: str
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[date] = None
    page_count: Optional[int] = None
    language: Optional[str] = None

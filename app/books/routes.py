from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from typing import List

from app.books.schemas import Book, BookUpdateModel
from app.books.book_db import db


book_router = APIRouter()


# get all books
@book_router.get("/", response_model=List[Book])
async def get_all_books():
    return db


# get a book using book_id from DB
@book_router.get("/{book_id}")
async def get_book(book_id: int) -> dict:
    for book in db:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")


# add a book in database
@book_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(data: Book) -> dict:
    new_book = data.model_dump()
    db.book_routerend(new_book)
    return new_book


# update a particular DB
@book_router.patch("/{book_id}")
async def update_book(book_id: int, book_update_data: BookUpdateModel) -> dict:
    for book in db:
        if book["id"] == book_id:
            if book_update_data.title:
                book["title"] = book_update_data.title
            if book_update_data.author:
                book["author"] = book_update_data.author
            if book_update_data.publisher:
                book["publisher"] = book_update_data.publisher
            if book_update_data.publish_date:
                book["publish_date"] = book_update_data.publish_date
            if book_update_data.page_count:
                book["page_count"] = book_update_data.page_count
            if book_update_data.language:
                book["language"] = book_update_data.language

            return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")


# delete a book from DB
@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in db:
        if book["id"] == book_id:
            db.remove(book)
            return {}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")

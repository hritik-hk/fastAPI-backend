from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID


from .schemas import Book, BookUpdateModel, BookCreateModel
from .service import BookService
from app.database.main import get_session
from app.auth.dependencies import AccessTokenBearer, RoleChecker


book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


# get all books
@book_router.get("/", response_model=List[Book], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books


# get a book using book_id from DB
@book_router.get("/{book_id}", response_model=Book, dependencies=[role_checker])
async def get_book(
    book_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
) -> dict:
    book = await book_service.get_book(book_id, session)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    else:
        return book


# add a book in database
@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
) -> dict:
    new_book = await book_service.create_book(book_data, session)
    if new_book:
        return new_book
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="could not create book",
        )


# update a particular DB
@book_router.patch("/{book_id}", response_model=Book, dependencies=[role_checker])
async def update_book(
    book_id: UUID,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
) -> dict:
    updated_book = await book_service.update_book(book_id, book_update_data, session)
    if updated_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="book not found"
        )
    else:
        return updated_book


# delete a book from DB
@book_router.delete(
    "/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
):
    deleted_book = await book_service.delete_book(book_id, session)
    if deleted_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="book not found"
        )
    else:
        return delete_book

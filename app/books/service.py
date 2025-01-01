from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from .models import Book
from datetime import datetime


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, user_id: UUID, session: AsyncSession):
        statement = (
            select(Book).where(Book.user_id == user_id).order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_id: UUID, session: AsyncSession):
        statement = select(Book).where(Book.id == book_id)
        result = await session.exec(statement)
        book = result.first()

        return book if book is not None else None

    async def create_book(
        self, book_data: BookCreateModel, user_id: str, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.publish_date = datetime.strptime(
            book_data_dict["publish_date"], "%Y-%m-%d"
        )
        new_book.user_id = user_id
        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, book_id: UUID, update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_book(book_id, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump()
            for key, val in update_data_dict.items():
                if val:
                    setattr(book_to_update, key, val)
            await session.commit()
            return book_to_update
        else:
            return None

    async def delete_book(self, book_id: UUID, session: AsyncSession):
        book_to_delete = await self.get_book(book_id, session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return book_to_delete
        else:
            return None

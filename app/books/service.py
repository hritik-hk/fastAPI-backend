from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from .models import Book


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_id: UUID, session: AsyncSession):
        statement = select(Book).where(Book.id == book_id)
        result = await session.exec(statement)
        book = result.first()

        return book if book is not None else None

    async def create_book(self, book_data: BookCreateModel, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)

        session.add(new_book)
        await session.commit()

    async def update_bool(
        self, book_id: UUID, update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = self.get_book(book_id, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump()
            for key, val in update_data_dict.items():
                setattr(book_to_update, key, val)
            await session.commit()
            return book_to_update
        else:
            return None

    async def delete_book(self, book_id: UUID, session: AsyncSession):
        book_to_delete = self.get_book(book_id, session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return book_to_delete
        else:
            return None

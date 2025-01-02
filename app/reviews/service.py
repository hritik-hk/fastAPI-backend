from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from sqlmodel import select, desc
import uuid
import logging

from app.database.models import Review
from app.auth.service import UserService
from app.books.service import BookService
from .schemas import ReviewCreateModel


book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_id: uuid.UUID,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_id=book_id, session=session)
            user = await user_service.get_user_by_email(
                email=user_email, session=session
            )

            review_data_dict = review_data.model_dump()

            if not book:
                raise HTTPException(
                    detail="Book not found", status_code=status.HTTP_404_NOT_FOUND
                )

            if not user:
                raise HTTPException(
                    detail="User not found", status_code=status.HTTP_404_NOT_FOUND
                )

            new_review = Review(**review_data_dict, user=user, book=book)

            session.add(new_review)

            await session.commit()

            return new_review

        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong on server",
            )

    async def get_review(self, review_id: str, session: AsyncSession):
        statement = select(Review).where(Review.id == review_id)

        result = await session.exec(statement)

        return result.first()

    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))

        result = await session.exec(statement)

        return result.all()

    async def delete_review_to_from_book(
        self, review_id: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(user_email, session)

        review = await self.get_review(review_id, session)

        if not review or (review.user != user):
            raise HTTPException(
                detail="you cannot delete this review",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        session.delete(review)

        await session.commit()

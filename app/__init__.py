from fastapi import FastAPI
from app.books.routes import book_router

VERSION = "v1"

app = FastAPI(
    version=VERSION, title="Bookly", description="REST APIs for book web service"
)

app.include_router(book_router, prefix="/api/{VERSION}/books", tags="books")

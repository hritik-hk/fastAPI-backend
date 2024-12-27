from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.configs.settings import VERSION, SERVER_HOST, SERVER_PORT
from app.database.main import init_db

# routes
from app.books.routes import book_router
from app.auth.routes import auth_router


@asynccontextmanager
async def lifeSpan_events(app: FastAPI):
    print(f"server starting on port: {SERVER_PORT}")
    await init_db()
    yield


def initialize_backend_application(lifespan_events) -> FastAPI:
    app = FastAPI(
        version=VERSION,
        title="Bookly",
        description="REST APIs for book web service",
        docs_url="/docs",
        lifespan=lifespan_events,
    )

    app.include_router(auth_router, prefix=f"/api/{VERSION}/auth", tags="auth")
    app.include_router(book_router, prefix=f"/api/{VERSION}/books", tags="books")

    return app


app: FastAPI = initialize_backend_application(lifeSpan_events)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)

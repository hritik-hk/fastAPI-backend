from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from app.database.redis import redis_client

RATE_LIMIT = 100  # number of requests allowed in timeframe
TIME_WINDOW = 60  # time window in seconds 


def register_middlewares(app: FastAPI):
    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        if not redis_client:
            logging.error(msg="redis client is not initialized")
            JSONResponse(
                {"error": "something went wrong"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        client_ip = request.client.host
        url_path = request.url.path
        redis_key = f"rate_limit: {client_ip} {url_path}"

        # check for count
        current_count = await redis_client.get(redis_key)
        if current_count is None:
            # init count and set expiry for this key
            await redis_client.set(redis_key, 1, ex=TIME_WINDOW)
        else:
            current_count = int(current_count)
            if current_count >= RATE_LIMIT:
                return JSONResponse(
                    {"error": "Too many requests, try again later."},
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            await redis_client.incr(redis_key)

        # proceeds to the next middleware or route
        response = await call_next(request)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
        ],
    )

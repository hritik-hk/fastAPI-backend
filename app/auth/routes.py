from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime


from .schemas import UserCreateModel, UserModel, UserLoginModel
from .service import UserService
from app.database.main import get_session
from .utils import create_access_token, verify_password
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from app.database.redis import add_jwtId_to_blocklist


auth_router = APIRouter()
user_service = UserService()
role_checker = Depends(RoleChecker(["admin", "user"]))


@auth_router.post(
    "/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user with this email already exists",
        )
    else:
        new_user = await user_service.create_user(user_data, session)
        return new_user


@auth_router.post("/login")
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        # validate password
        isValid = verify_password(password, hash=user.password_hash)
        if isValid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "role": user.role,
                    "userId": str(user.id),
                }
            )

            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    "role": user.role,
                    "userId": str(user.id),
                },
                expiry=timedelta(days=2),
                refresh=True,
            )

            return JSONResponse(
                content={
                    "message": "login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "username": user.username},
                }
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"message": "invalid email or password"},
    )


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid or expired token"
        )
    else:
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})


@auth_router.get("/me", response_model=UserModel, dependencies=[role_checker])
async def get_current_user(user=Depends(get_current_user)):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jwtId = token_details["jwtId"]
    await add_jwtId_to_blocklist(jwtId)

    return JSONResponse(content={"message": "logged out successfully"})

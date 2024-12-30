from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from datetime import timedelta


from .schemas import UserCreateModel, UserModel, UserLoginModel
from .service import UserService
from app.database.main import get_session
from .utils import create_access_token, verify_password


auth_router = APIRouter()
user_service = UserService()


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
                user_data={"email": user.email, "userId": str(user.id)}
            )

            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    "userId": user.id,
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

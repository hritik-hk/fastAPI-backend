from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime


from .schemas import (
    UserCreateModel,
    UserLoginModel,
    UserBookModel,
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
)
from .service import UserService
from app.database.main import get_session
from .utils import (
    create_access_token,
    verify_password,
    create_url_safe_token,
    decode_url_safe_token,
    generate_passwd_hash,
)
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from app.database.redis import add_jwtId_to_blocklist
from app.errors import UserAlreadyExists, InvalidCredentials, InvalidToken, UserNotFound
from app.mail import mail, create_message
from app.config import Config
from app.celery import send_email


auth_router = APIRouter()
user_service = UserService()
role_checker = Depends(RoleChecker(["admin", "user"]))


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()
    else:
        await user_service.create_user(user_data, session)

        token = create_url_safe_token({"email": email})

        link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

        html_message = f""" 
        <h1>Verify your email</h1>
        <p>Click this <a href="{link}">link</a>  to verify your email</p>
        """
        subject = "Verify Your email - Bookhub"
        send_email
        send_email.delay([email], subject, html_message)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Account created, Check email for account verification",
            },
        )


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


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

    raise InvalidCredentials()


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) < datetime.now():
        raise InvalidToken()
    else:
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})


@auth_router.get("/me", response_model=UserBookModel, dependencies=[role_checker])
async def get_current_user(user=Depends(get_current_user)):
    return user


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password - BookHub"
    send_email.delay([email], subject, html_message)

    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        passwd_hash = generate_passwd_hash(new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jwtId = token_details["jwtId"]
    await add_jwtId_to_blocklist(jwtId)

    return JSONResponse(content={"message": "logged out successfully"})

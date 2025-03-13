from auth.schemas import (EmailModel, SUserAddDB, SUserAuth, SUserInfo,
                          SUserRegister)
from auth.utils import authenticate_user, hash_password, set_tokens
from core import db_helper
from core.exceptions import exc
from crud.users import UsersDAO
from dependencies.dep_auth import check_refresh_token, get_current_user
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/")
async def register_user(
    user_data: SUserRegister,
    session: AsyncSession = Depends(db_helper.get_session_with_commit),
) -> dict:
    # Проверка существования пользователя
    user_dao = UsersDAO(session)
    existing_user = await user_dao.find_one_or_none(
        filters=EmailModel(email=user_data.email)
    )
    if existing_user:
        raise exc.user_exists
    # Подготовка данных для добавления
    user_data_dict = user_data.model_dump()
    user_data_dict.pop("confirm_password", None)
    # Хеширование пароля (пароль остается строкой)
    user_data_dict["password"] = hash_password(user_data_dict["password"])
    # Добавление пользователя
    await user_dao.add(values=SUserAddDB(**user_data_dict))
    return {"message": "Вы успешно зарегистрированы!"}


@router.post("/login/")
async def auth_user(
    response: Response,
    user_data: SUserAuth,
    session: AsyncSession = Depends(db_helper.get_session_without_commit),
) -> dict:
    users_dao = UsersDAO(session)
    user = await users_dao.find_one_or_none(filters=EmailModel(email=user_data.email))
    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise exc.invalid_email_or_password
    set_tokens(response, user.id)
    return {"ok": True, "message": "Авторизация успешна!"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Пользователь успешно вышел из системы"}


@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)) -> SUserInfo:
    return SUserInfo.model_validate(user_data)


@router.post("/refresh")
async def process_refresh_token(
    response: Response, user: User = Depends(check_refresh_token)
):
    set_tokens(response, user.id)
    return {"message": "Токены успешно обновлены"}

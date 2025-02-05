from datetime import datetime, timezone
from fastapi import Request, Depends
from jwt import PyJWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from users.models import User
from auth.utils import decode_jwt
from core.exceptions import exc
from core import db_helper

from crud.users import UsersDAO
from core.exceptions import exc


def get_access_token(request: Request) -> str:
    token = request.cookies.get('access_token')
    # logger.info(f"Извлекаем из куки access_token: {token}")
    if not token:
        raise exc.token_not_found
    return token


def get_refresh_token(request: Request) -> str:
    token = request.cookies.get('refresh_token')
    # logger.info(f"Извлекаем из куки refresh_token: {token}")
    if not token:
        raise exc.token_not_found
    return token


async def check_refresh_token(
        token: str = Depends(get_refresh_token),
        session: AsyncSession = Depends(db_helper.get_session_without_commit)
) -> User:
    logger.info(f"Проверяем refresh_token и возвращаем пользователя.")
    try:
        payload = decode_jwt(token=token)
        user_id = payload.get("sub")
        if not user_id:
            raise exc.user_id_not_found
        user = await UsersDAO(session).find_one_or_none_by_id(data_id=int(user_id))
        if not user:
            raise exc.user_not_found
        return user
    except PyJWTError:
        raise exc.invalid_jwt


async def get_current_user(
        token: str = Depends(get_access_token),
        session: AsyncSession = Depends(db_helper.get_session_without_commit)
) -> User:
    # logger.info(f"Проверяем access_token и возвращаем пользователя.")
    try:
        payload = decode_jwt(token=token) # Декодируем токен
    except ExpiredSignatureError:
        raise exc.token_expired
    except PyJWTError:
        raise exc.invalid_jwt # Общая ошибка для токенов
    
    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    # logger.info(f"Проверяем срок годности токена: истекает - {expire_time} текущее время - {datetime.now(timezone.utc)}")
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise exc.token_expired
    
    user_id: str = payload.get('sub')
    if not user_id:
        raise exc.user_id_not_found
    
    user = await UsersDAO(session).find_one_or_none_by_id(data_id=int(user_id))
    if not user:
        raise exc.user_not_found
    
    return user
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import Response
from loguru import logger

from core.config import settings


def create_tokens(data: dict) -> dict:
    # AccessToken
    access_token = encode_jwt(
        payload={**data, "type": "access"},
        # expire_delta=timedelta(seconds=10)  # Для отладки (10 секунд)
        expire_delta=timedelta(minutes=settings.auth.token_expire_minutes)  # Продакшен
    )
    # RefreshToken
    refresh_token = encode_jwt(
        payload={**data, "type": "refresh"},
        expire_delta=timedelta(days=settings.auth.token_expire_days)
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


def encode_jwt(
        payload: dict,
        private_key: str = settings.auth.private_key.read_text(),
        algorithm: str = settings.auth.algorithm,
        expire_delta: timedelta | None = None,
    ):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_delta:
        expire = now + expire_delta
    else:
        # Значение по умолчанию (на случай прямого вызова encode_jwt)
        expire = now + timedelta(minutes=15)
    to_encode["exp"] = expire
    # Добавляем время создания токена (iat)
    to_encode.setdefault("iat", now)
    encoded_jwt = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm
    )
    return encoded_jwt


def decode_jwt(
        token: str | bytes, 
        public_key: str = settings.auth.public_key.read_text(), 
        algorithm: str = settings.auth.algorithm,
    ):
    decode = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )
    logger.info(f"Получаем декод токена: {decode}")
    return decode


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password_bytes: bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_password = hashed_password_bytes.decode('utf-8')
    logger.info(f"Хешированный пароль: {hashed_password}")
    return hashed_password


def validate_password(password: str, hashed_password: str) -> bool:
    try:
        password_bytes: bytes = password.encode('utf-8')
        hashed_password_bytes: bytes = hashed_password.encode('utf-8')
        # logger.info(f"Введенный пароль: {password}")
        # logger.info(f"Хеш из базы данных: {hashed_password}")
        valid_pass: bool = bcrypt.checkpw(password_bytes, hashed_password_bytes)
        # if not valid_pass:
        #     logger.error(f"Пароль из формы: {password} != пароль из БД: {hashed_password} – Не равны...")
        return valid_pass
    except Exception as e:
        logger.error(f"Ошибка при проверке пароля: {e}")
        return False


async def authenticate_user(user, password):
    if not user:
        logger.error("Пользователь не найден")
        return None
    if validate_password(password=password, hashed_password=user.password) is False:
        logger.error("Неверный пароль")
        return None
    return user


def set_tokens(response: Response, user_id: int):
    new_tokens = create_tokens(data={"sub": str(user_id)})
    access_token = new_tokens.get('access_token')
    refresh_token = new_tokens.get("refresh_token")
    # logger.info(f"Вход в систему с access_toke: {access_token} и refresh_token: {refresh_token}")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        # secure=True, # Работает только с запросами через https
        # samesite="lax",
        max_age=3600 * 24 * 7,  # Срок жизни куки (например, 7 дней)
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        # secure=True, # Работает только с запросами через https
        # samesite="lax",
        max_age=3600 * 24 * 7,  # Срок жизни куки (например, 7 дней)
        path="/",
    )
from fastapi import status, HTTPException


class Exceptions:
    # Пользователь уже существует
    user_exists = HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует"
    )

    # Пользователь не найден
    user_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
    )

    # Отсутствует идентификатор пользователя
    user_id_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Отсутствует идентификатор пользователя",
    )

    # Неверная почта или пароль
    invalid_email_or_password = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Неверная почта или пароль"
    )

    # Токен истек
    token_expired = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истек"
    )

    # Некорректный формат токена
    invalid_token_format = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Некорректный формат токена"
    )


    # Токен отсутствует в заголовке
    token_not_found = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Токен отсутствует в заголовке"
    )

    # Невалидный JWT токен
    invalid_jwt = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не найден"
    )

    # Недостаточно прав
    forbidden = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав"
    )

    invalid_format_token = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Неверный формат токена. Ожидается 'Bearer <токен>'",
    )
    
exc = Exceptions()

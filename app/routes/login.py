from datetime import datetime, timedelta, timezone
import inspect

from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json
from sanic.log import logger
from sanic import Blueprint

import bcrypt
import jwt

app_salt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWJjIiwiZW1haWwiOiJuYW5jeUBnbWFpbC5jb20iLCJleHAiOjE2NjgzNzExNTZ9.eAaFT-H8PfLpRKpY37xk7frAfJnQS5jn7hjycOpOj3o".encode('utf-8')
secret = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWJjIiwiZW1haWwiOiJuYW5jeUBnbWFpbC5jb20iLCJleHAiOjE2NjgzNzIzNzJ9.zyXSZ6lwtBCHN8Jwf5aFzHE4_uwVNmUcHOvjJ72AImo"
users = {
    "aqua": bcrypt.hashpw(app_salt, "NjgzNzExNTZ9.eAaFT-H8P".encode('utf-8')),
    "arena": bcrypt.hashpw(app_salt, "zI1NiIsInR5cCI6IkpXVCJ9.eyJ1".encode('utf-8')),
}


async def verify_password(username, password):
    try:
        byte_password = password.encode('utf-8')
        hashed_password = users.get(username)
        if bcrypt.checkpw(byte_password, hashed_password):
            return True
        else:
            logger.info(f"check_user. password for {username} is invalid")
            return None
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return None


async def gen_token():
    dt = datetime.now(tz=timezone.utc) + timedelta(days=2)
    return jwt.encode({'exp': dt}, secret, algorithm='HS256')


async def verify_token(token):
    try:
        jwt.decode(token, secret, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError as e:
        logger.error(f"verify_token - {e}")
        return False

bp = Blueprint("login")


@bp.route("/login")
@openapi.definition(
    secured={"basicAuth": []},
    summary="Получение токена",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def login(request):
    """Получение токена

    Для работы с API необходимо
    - получить токен
    - в *header* последующих запросах указать **'Authorization' => 'Bearer *token*'**

    Получение токена осуществляется на основе **базовой аутентификации**.

    openapi:
    ---
    operationId: login
    tags:
      - Login
    """

    try:
        username = request.credentials._username
        password = request.credentials._password
        if not await verify_password(username, password):
            return text(f"Basic Authentication error", status=400)

        if token := await gen_token():
            return text(token)
        else:
            return text(f"Bearer Authentication error", status=400)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return text(f"{e}", status=400)

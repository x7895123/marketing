from datetime import datetime, timedelta, timezone
import inspect
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json, Request
from sanic.log import logger
from sanic import Blueprint

import bcrypt
import jwt

app_salt = b'$2b$12$iRF76B96HrCFH9HNEpNQpe'
secret = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWJjIiwiZW1haWwiOiJuYW5jeUBnbWFpbC5j"
users = {
    "aqua_aqua": bcrypt.hashpw("NjgzNzExNTZ9.eAaFT-H8P".encode('utf-8'), app_salt),
    "arena": bcrypt.hashpw("zI1NiIsInR5cCI6IkpXVCJ9.eyJ1".encode('utf-8'), app_salt),
    "kiiik": bcrypt.hashpw("LYCbYsgRb-".encode('utf-8'), app_salt),
}


async def verify_password(request):
    try:
        username = request.credentials.username
        password = request.credentials.password
        byte_password = password.encode('utf-8')
        hashed_password = users.get(username)
        if bcrypt.checkpw(byte_password, hashed_password):
            return True
        else:
            logger.info(f"check_user. password for {username} is invalid")
            return False
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return False


async def gen_token(company):
    dt = datetime.now(tz=timezone.utc) + timedelta(days=2)
    return jwt.encode(
        {'exp': dt, 'company': company},
        secret,
        algorithm='HS256'
    )


async def verify_token(request):
    try:
        decoded = jwt.decode(request.token, secret, algorithms=["HS256"])
        request.ctx.company = decoded['company']
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
async def login(request: Request):
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
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        if token := await gen_token(request.ctx.company):
            return text(token)
        else:
            return text(f"Getting Bearer Authentication error", status=400)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return text(f"login error: {e}", status=400)

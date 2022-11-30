from datetime import datetime, timedelta, timezone
import inspect
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json, Request
from sanic.log import logger
from sanic import Blueprint

import bcrypt
import jwt

from ..services import marketing_db

app_salt = b'$2b$12$iRF76B96HrCFH9HNEpNQpe'
secret = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWJjIiwiZW1haWwiOiJuYW5jeUBnbWFpbC5j"
# users = {
#     "puppeteer": bcrypt.hashpw("rf;lsq j[jnybr ;tkftn pyfnm? ult cblbn afpfy".encode('utf-8'), app_salt),
#     "guest": bcrypt.hashpw("kj[".encode('utf-8'), app_salt),
#     "aqua": bcrypt.hashpw("iIsInR5cCI6IkpX".encode('utf-8'), app_salt),
#     "aqua_aqua": bcrypt.hashpw("1".encode('utf-8'), app_salt),
#     "arena": bcrypt.hashpw("zI1NiIsInR5cCI6IkpXVCJ9.eyJ1".encode('utf-8'), app_salt),
#     "kiiik": bcrypt.hashpw("LYCbYsgRb-".encode('utf-8'), app_salt),
# }

users = {
    "puppeteer": "rf;lsq j[jnybr ;tkftn pyfnm? ult cblbn afpfy",
    "guest": "kj[",
    "aqua": "iIsInR5cCI6IkpX",
    "aqua_aqua": "1",
    "arena": "zI1NiIsInR5cCI6IkpXVCJ9.eyJ1",
    "kiiik": "LYCbYsgRb-",
}


async def verify_password(request, check_user=None):
    try:
        entered_username = request.credentials.username
        entered_password = request.credentials.password

        if check_user and check_user != entered_username:
            return False

        if await marketing_db.check_user(
                username=entered_username, password=entered_password
        ):
            return entered_username == check_user if check_user else True

        return False
        # byte_password = password.encode('utf-8')
        # hashed_password = users.get(username)
        # saved_password = await marketing_db.get_password_hash(username)
        # if bcrypt.checkpw(byte_password, hashed_password):
        #     return username == check_user if check_user else True
        # else:
        #     logger.info(f"check_user. password for {username} is invalid")
        #     return False
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


@bp.route("/user_list", methods=["GET", "OPTIONS"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Получение user list",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def user_list(request: Request):
    """Получение user list

    openapi:
    ---
    operationId: puppets
    tags:
      - Login
    """

    try:
        if not await verify_password(request=request, check_user='puppeteer'):
            return text(f"Basic Authentication error", status=400)

        return json(await marketing_db.get_users())
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return text(f"error: {e}", status=400)


@bp.route("/assign_user_code", methods=["POST", "OPTIONS"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Получение user list",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def assign_user_code(request: Request):
    """Получение user list

    openapi:
    ---
    operationId: puppets
    tags:
      - Login
    """

    try:
        if not await verify_password(request=request, check_user='puppeteer'):
            return text(f"Basic Authentication error", status=400)

        username = request.json.get('username')
        code = request.json.get('code')
        if await marketing_db.assign_user_code(username=username, code=code):
            return text("ok", status=200)
        else:
            return text("error: assign user code failed", status=400)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return text(f"error: {e}", status=400)


@bp.route("/get_authorization", methods=["POST", "OPTIONS"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Получение user list",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def get_authorization(request: Request):
    """Получение user list

    openapi:
    ---
    operationId: puppets
    tags:
      - Login
    """

    try:
        if not await verify_password(request=request, check_user='puppeteer'):
            return text(f"Basic Authentication error", status=400)

        code = request.json.get('code')
        authorization = await marketing_db.get_authorization(code=code)
        if authorization:
            return text(authorization, status=200)
        else:
            return text("error: get authorization failed", status=400)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return text(f"error: {e}", status=400)

if __name__ == '__main__':
    pass

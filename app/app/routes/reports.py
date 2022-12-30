import inspect
from urllib.parse import unquote
import rapidjson
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json, Request
from sanic.log import logger
from sanic import Blueprint

from ..routes.login import verify_password
from ..services import marketing_db

bp = Blueprint("reports")


@bp.route("/wheel_report", methods=["POST", "OPTIONS"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Add User",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def wheel_report(request: Request):
    """add user

    openapi:
    ---
    operationId: add_user
    tags:
      - Admin
    """

    try:
        if not await verify_password(request=request, check_user='puppeteer'):
            return text(f"Basic Authentication error", status=400)



        logger.info(f"add_user request.json: {request.body}")
        body = unquote(request.body)
        body = rapidjson.loads(body)

        name = body.get('name')
        password = body.get('password')
        company = body.get('company')
        cashdesk = body.get('cashdesk')

        if await marketing_db.add_user(name=name, password=password, company=company, cashdesk=cashdesk):
            return text("ok", status=200)
        else:
            return text("error: add user failed", status=400)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return text(f"error: {e}", status=400)



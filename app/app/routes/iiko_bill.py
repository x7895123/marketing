import inspect
import uuid

import rapidjson
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json
from sanic.log import logger
from sanic import Blueprint

from ..routes.models.bill import DemoBill
from ..routes.login import verify_password, verify_token
from ..services import marketing_db

bp = Blueprint("iiko_bill")


@bp.route("/iiko_bill", methods=["POST"])
@openapi.definition(
    tag="Integrator",
    secured={"basicAuth": []},
    summary="Добавление счета iiko",
    body=definitions.RequestBody(DemoBill, required=True),
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def iiko_bill(request):

    try:
        logger.info(f"start add_bill")
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        logger.info(f"request.ctx.company: {request.ctx.company}")
        logger.info(f"Sending gift request.json: {request.body}")



        return json({"result": "ok"}, status=200)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json({f"error": e}, status=400)
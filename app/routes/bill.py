import inspect

import rapidjson
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json
from sanic.log import logger
from sanic import Blueprint

from app.rabbit.rabbit import Rabbit
from app.routes.login import verify_password
from app.services import dostyq_marketing
from app.services.dostyq_marketing import send_gift_results
from app.services import marketing_db
from app.shared import settings, tools

bp = Blueprint("bill")


@bp.route("/add_bill", methods=["POST"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Добавление счета",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def add_bill(request, publisher: Rabbit):
    """Получение текущего задания для Фортуны

    Получение задания осуществляется на основе **базовой аутентификации**.

    openapi:
    ---
    operationId: get_spin
    tags:
      - Game
    """

    try:
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        marketing_bill, marketing_cashback = await marketing_db.add_bill(request.json, request.ctx.company)
        if body := result.get('body'):
            cashdesk = body.get('cashdesk')
            await publisher.publish(body=body, queue_name=f'{cashdesk}_calc_bonus')
            return json(f"get_spin", status=200)
        else:
            return json(body, status=400 if body.get('error') else 400)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json({f"get_spin error": e}, status=400)


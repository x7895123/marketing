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
from app.shared import settings, tools

bp = Blueprint("game")


@bp.route("/get_spin", methods=["POST"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Получение текущего задания для Фортуны",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def get_spin(request, publisher: Rabbit):
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

        cashdesk = request.json.get('cashdesk')
        message = await publisher.get(f'{cashdesk}_spin')
        if message:
            return json(message)
        else:
            return json({})
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json(f"get_spin error", status=400)


@bp.route("/send_gift", methods=["POST"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Send a gift",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def send_gift(request):
    """Send Gift

    openapi:
    ---
    operationId: send_gift
    tags:
      - Game
    """

    try:
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        gift = request.json
        phone = request.json.get('phone')
        if not phone:
            return text(f"phone is required", status=401)

        phone = tools.correct_phone(phone)

        bill_id = gift.get('bill_id')
        if not bill_id:
            return text(f"bill_id is required", status=401)

        source = gift.get('source', 'aqua_marketing')

        gift.update({
            "phone": phone,
            "source": source,
        })
        aqua_auth = settings.get(f"dostyq_marketing_authorization/{request.credentials.username}")
        result = await dostyq_marketing.send_gift(
            dostyq_marketing_authorization=aqua_auth,
            gift=gift
        )
        return text(send_gift_results.get(result), status=400 if result == -1 else 200)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return text(f"send_gift error", status=400)

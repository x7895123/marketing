import inspect

import rapidjson
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json
from sanic.log import logger
from sanic import Blueprint

from app.models import bills
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
async def add_bill(request):
    """Получение текущего задания для Фортуны

    Получение задания осуществляется на основе **базовой аутентификации**.

    openapi:
    ---
    operationId: get_spin
    tags:
      - Game
    """

    try:
        logger.info(f"start add_bill")
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        logger.info(f"request.ctx.company: {request.ctx.company}")

        body = await marketing_db.add_bill(request.json, request.ctx.company)
        if body.get('error'):
            return json({"error": body.get('error')}, status=400)
        elif body.get('published'):
            return json({"result": "already published"}, status=200)
        logger.info(body)

        calc_bonus_queue_name = f'{body.get("cashdesk")}_calc_bonus'
        if await request.app.ctx.publisher.publish(
                body=rapidjson.dumps(body),
                queue_name=calc_bonus_queue_name
        ):
            await bills.MarketingGift.filter(id=body.get('gift_id')).update(published=True)
            # await marketing_db.update_cashback(body.get('id_cashback'), {'published': True})
            return json({"result": "ok"}, status=200)
        else:
            return json({"error": f"can't publish to {calc_bonus_queue_name}"}, status=400)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json({f"error": e}, status=400)

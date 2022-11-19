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
        if marketing_cashback[1]:
            body = {}

            company = marketing_bill[0].__dict__.get("company")
            cashdesk = marketing_bill[0].__dict__.get("cashdesk")
            bill_id = marketing_bill[0].__dict__.get("bill_id")
            phone = marketing_bill[0].__dict__.get("phone")
            amount = marketing_bill[0].__dict__.get("amount")
            paytime = marketing_bill[0].__dict__.get("paytime")
            paytime = paytime.strftime("%Y-%m-%d %H:%M:%S")
            original_bill = marketing_bill[0].__dict__.get("original_bill")
            task = marketing_bill[0].__dict__.get("task")
            id_cashback = marketing_cashback[0].__dict__.get('id')
            cashback_create_ts = marketing_cashback[0].__dict__.get('create_ts')
            cashback_create_ts = cashback_create_ts.strftime("%Y-%m-%d %H:%M:%S")
            body.update({
                "company": company,
                "cashdesk": cashdesk,
                "bill_id": bill_id,
                "phone": phone,
                "amount": amount,
                "paytime": paytime,
                "original_bill": original_bill,
                "task": task,
                'id_cashback': id_cashback,
                'cashback_create_ts': cashback_create_ts,
                'source': 'cashback'
            })
            logger.info(body)
            body = rapidjson.dumps(body)
            await publisher.publish(body=body, queue_name=f'{cashdesk}_calc_bonus')
            return json({"result": "ok"}, status=200)
        else:
            return json({"result": "already saved"}, status=200)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json({f"error": e}, status=400)

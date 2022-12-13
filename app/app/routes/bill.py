import inspect
import uuid

import rapidjson
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json
from sanic.log import logger
from sanic import Blueprint

from ..routes.login import verify_password, verify_token
from ..services import marketing_db

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
    operationId: add_bill
    tags:
      - Integration
    """

    try:
        logger.info(f"start add_bill")
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        logger.info(f"request.ctx.company: {request.ctx.company}")

        bill = await marketing_db.add_bill(request.json, request.ctx.company)
        logger.info(f"bill_id: {bill.id}")
        if not bill:
            return text(f"error add bill: {request.json}", status=400)
        elif bill.published:
            logger.info(f"bill already published: {request.json}")
            return text(f"bill already published: {request.json}", status=200)

        calc_bonus_queue_name = f'{request.ctx.company}_calc_bonus'
        logger.info(f"calc_bonus_queue_name: {calc_bonus_queue_name}")
        if await request.app.ctx.publisher.publish(
                body=rapidjson.dumps({"bill_id": bill.id}),
                queue_name=calc_bonus_queue_name
        ):
            bill.published = True
            await bill.save()
            return json({"result": "ok"}, status=200)
        else:
            return json(
                {"error": f"can't publish to {calc_bonus_queue_name}"},
                status=400
            )
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json({f"error": e}, status=400)


@bp.route("/transfer", methods=["POST"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Transfer tokens",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def transfer(request):
    """Transfer tokens

    Transfer tokens осуществляется на основе **базовой аутентификации**.

    openapi:
    ---
    operationId: get_spin
    tags:
      - Game
    """

    try:
        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                    f'{inspect.stack()[0][3]}: start')
        if not await verify_token(request=request):
            return text(f"Bearer Authentication error", status=400)

        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                    f'{inspect.stack()[0][3]}: company: {request.ctx.company}')

        """
            company=company,
            cashdesk=cashdesk,
            company_bill_id=company_bill_id,
            phone=phone,
            amount=amount,
            paytime=paytime,
            original_bill=bill,
            deal=deal
        """

        token = request.json.get('token')
        if str(token).lower() == 'arena_500':
            deal = {"ids1": [2], "amounts1": [500], "msg": "You got this! 🎮"}
        elif str(token).lower() == 'aqua_child':
            deal = {"ids1": [59], "amounts1": [1], "msg": "You got this! 🏊‍"}
        else:
            deal = request.json.get('deal')

        bill_body = {
            "company": request.ctx.company,
            "cashdesk": request.ctx.company,
            "company_bill_id": str(uuid.uuid4()),
            "phone": request.json.get("phone"),
            "amount": 0,
            "deal": deal
        }

        bill = await marketing_db.add_bill(bill_body, request.ctx.company)
        logger.info(f"bill_id: {bill.id}")
        if not bill:
            return text(f"error add bill: {request.json}", status=400)
        elif bill.published:
            logger.info(f"bill already published: {request.json}")
            return text(f"bill already published: {request.json}", status=200)

        calc_bonus_queue_name = f'{request.ctx.company}_calc_bonus'
        logger.info(f"calc_bonus_queue_name: {calc_bonus_queue_name}")
        if await request.app.ctx.publisher.publish(
                body=rapidjson.dumps({"bill_id": bill.id}),
                queue_name=calc_bonus_queue_name
        ):
            bill.published = True
            await bill.save()
            return json({"result": "ok"}, status=200)
        else:
            return json(
                {"error": f"can't publish to {calc_bonus_queue_name}"},
                status=400
            )
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json({f"error": e}, status=400)

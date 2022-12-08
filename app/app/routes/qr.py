import inspect
from urllib.parse import unquote
import rapidjson
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json
from sanic.log import logger
from sanic import Blueprint

from ..models import bills
from ..routes.login import verify_password
from ..services import marketing_db
from ..shared.draw_qr import create_qr

bp = Blueprint("qr")


@bp.route("/get_bill_qr", methods=["GET", "POST", "OPTIONS"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Получение текущего задания для Фортуны",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def get_bill_qr(request):
    """Получение текущего задания для Фортуны

    Получение задания осуществляется на основе **базовой аутентификации**.

    openapi:
    ---
    operationId: get_spin
    tags:
      - Game
    """

    try:
        # if request.ip != '192.168.90.10':
        # if not await verify_password(request=request):
        #     return text(f"Basic Authentication error", status=400)

        logger.info(f"get_bill_qr: {request.ctx.company}")
        company_bill_id = await marketing_db.add_bill_qr(request.ctx.company)
        logger.info(f"company_bill_id: {company_bill_id}")
        qr = create_qr(company_bill_id,
                       from_color='#000000',
                       to_color='#000000')

        return text(qr)

    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json(f"get_spin error", status=400)



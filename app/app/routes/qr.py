import inspect
from urllib.parse import unquote
import rapidjson
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json, response
from sanic.log import logger
from sanic import Blueprint
import io

from ..models import bills
from ..routes.login import verify_password
from ..services import marketing_db
from ..services import qr_auth_service
from ..shared.draw_qr import create_qr

bp = Blueprint("qr")


@bp.route("/get_spin_qr", methods=["GET", "POST", "OPTIONS"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Получение текущего задания для Фортуны",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def get_spin_qr(request):
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
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        logger.info(f"get_bill_qr: {request.credentials.username}")
        request_id = await marketing_db.add_qr_auth(request.credentials.username, 'spin')
        logger.info(f"request_id: {request_id}")

        # data = {
        #     "action": "aquaV1",
        #     "queue": "aqua",
        #     "id": request_id,
        # }
        # data = rapidjson.dumps(data)
        data = f"https://qr.dostyq.app/?action=aquaV1&queue=aqua&id={request_id}"
        qr = create_qr(data)

        with io.BytesIO() as output:
            qr.save(output, format="PNG")
            contents = output.getvalue()
            return response.raw(contents)

    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json(f"get_spin error", status=400)


@bp.route("/qr_auth", methods=["POST", "OPTIONS"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="QR Authorization",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def qr_auth(request):
    """QR Authorization

    Получение задания осуществляется на основе **базовой аутентификации**.

    openapi:
    ---
    operationId: qr_auth
    tags:
      - QR
    """

    try:
        # if request.ip != '192.168.90.10':
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        logger.info(f"qr_auth: {request.ctx.company}")
        result = await qr_auth_service.process_qr_auth(
            body=request.json,
            publisher=request.app.ctx.publisher
        )
        logger.info(f"qr_auth: {rapidjson.dumps(result)}")
        return text(rapidjson.dumps(result), status=200 if result.get("status") == 0 else 400)
        # return text(result.get("message"), status=200 if result.get("status") == 0 else 400)

    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return text(f"error {e}", status=400)

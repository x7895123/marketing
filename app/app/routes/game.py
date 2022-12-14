import inspect
from urllib.parse import unquote
import rapidjson
from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions
from sanic import text, exceptions, json
from sanic.log import logger
from sanic import Blueprint

from .spin_items.items import items
from ..models import bills
from ..routes.login import verify_password

bp = Blueprint("game")


@bp.route("/get_spin", methods=["GET", "POST", "OPTIONS"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Получение текущего задания для Фортуны",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def get_spin(request):
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

        logger.info(f"Getting: {request.body}")

        spin_queue_name = f'{request.credentials.username}_spin'
        while message := await request.app.ctx.publisher.get(
                spin_queue_name
        ):
            # check if the winnings have been sent
            spin_dict = rapidjson.loads(message.body)
            logger.info(f"spin_dict: {spin_dict}")
            gift_id = spin_dict.get('gift_id')
            spin = await bills.MarketingGift.get(id=gift_id)
            logger.info(f"spin: {spin}")

            if not spin.published:
                # if not sent, publish again, in case the message disappears
                await request.app.ctx.publisher.ttl_publish(
                    body=rapidjson.dumps(spin_dict),
                    queue_name=spin_queue_name,
                    minutes=1
                )
                return json(spin_dict)
        else:
            return json({})
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json(f"get_spin error", status=400)


@bp.route("/get_items", methods=["GET", "OPTIONS"])
@openapi.definition(
    secured={"basicAuth": []},
    summary="Получение items Фортуны",
    response=[
        definitions.Response('Ok', status=200),
        definitions.Response('Authentication error', status=400)
    ],
)
async def get_items(request):
    """Получение items Фортуны

    Получение осуществляется на основе **базовой аутентификации**.

    openapi:
    ---
    operationId: get_items
    tags:
      - Game
    """

    try:
        # if request.ip != '192.168.90.10':
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        logger.info(f"get_items: {items.get(request.credentials.username)}")
        return json(items.get(request.credentials.username))
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return json(f"get_spin error", status=400)


@bp.route("/send_gift", methods=["POST", "OPTIONS"])
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
        # if request.ip != '192.168.90.10':
        if not await verify_password(request=request):
            return text(f"Basic Authentication error", status=400)

        logger.info(f"Sending gift request.json: {request.body}")
        body = unquote(request.body)
        body = rapidjson.loads(body)

        gift_dict = body
        gift_id = gift_dict.get('gift_id')
        ids1 = gift_dict.get('ids1')
        amounts1 = gift_dict.get('amounts1')
        msg = gift_dict.get('msg')
        if not msg:
            msg = "Құттықтаймыз!👏Поздравляем!"
        phone = gift_dict.get('phone')

        if not (gift_id and ids1 and amounts1):
            return text(f"gift_id, ids1, amounts1 are required", status=401)

        gift = await bills.MarketingGift.get(id=gift_id)
        if gift.published:
            logger.info(f"gift already published {phone}")
            return text(f"gift already published {phone}", status=400)

        deal = {
            'ids1': ids1,
            'amounts1': amounts1,
            'msg': msg,
        }
        gift.deal = deal
        gift.screen_msg = msg
        await gift.save()

        if await request.app.ctx.publisher.publish(
                body=rapidjson.dumps({'gift_id': gift.id}),
                queue_name='send_gift'
        ):
            gift.published = True
            await gift.save()
            logger.info(f"gift spin published {phone}")
            return text(f"gift spin published {phone}", status=200)
        else:
            return text(
                f"can't publish gift spin to send_gift {phone}",
                status=400
            )
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return text(f"send_gift error", status=400)

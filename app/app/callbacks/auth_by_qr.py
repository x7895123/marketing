import datetime
import inspect
import math
from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage

import rapidjson
from sanic.log import logger

from ..rabbit.rabbit import Rabbit
from ..shared.tools import clock_emoji

import os

if os.name == 'nt':
    from app.app.models import bills, qr_auth
    from app.app.shared import tools
else:
    from ..models import bills, qr_auth
    from ..shared import tools


async def process_qr_auth(message, publisher: Rabbit):
    result = {"status": 2, "message": "unrecognized"}
    try:
        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                    f'{inspect.stack()[0][3]}: start {message.body}')

        body_dict = rapidjson.loads(message.body)

        request_id = body_dict.get('uuid')
        phone = body_dict.get('phone')
        phone = tools.correct_phone(phone)
        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                    f'{inspect.stack()[0][3]}: data {request_id} {phone}')
        if phone:
            try:
                rec = await qr_auth.QrAuth.get(request_id=request_id)
                logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                            f'{inspect.stack()[0][3]}: rec.assignment {rec.assignment}')
                if rec.phone is None:
                    rec.phone = phone
                    if rec.assignment == 'spin':
                        marketing_bill = await bills.MarketingBill.get_or_create(
                            company=rec.username,
                            company_bill_id=request_id,
                            phone=phone
                        )
                        await marketing_bill[0].save()

                        if not await add_and_publish_spin(
                            company=rec.username,
                            bill_id=request_id,
                            phone=phone,
                            cashdesk=rec.username,
                            publisher=publisher
                        ):
                            result = {"status": 1, "message": "already_scanned"}
                else:
                    result = {"status": 1, "message": "already_scanned"}
                await rec.save()
            except Exception as e:
                logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
                result = {"status": 2, "message": "unrecognized"}
        else:
            logger.info(
                f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: phone is not defined')
            result = {"status": 1, "message": "phone_is _empty"}
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
    finally:
        if message.reply_to is not None and message.correlation_id is not None:
            logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]} '
                         f'reply_to: {message.reply_to} - {message.correlation_id}')

            logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]} '
                        f'result: {result}')

            response = rapidjson.dumps(result).encode()

            connection = await publisher.connect()
            channel = await connection.channel()
            exchange = channel.default_exchange

            await exchange.publish(
                Message(
                    body=response,
                    correlation_id=message.correlation_id,
                ),
                routing_key=message.reply_to,
            )
            logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]} '
                        f'sent result: {result}')

        await message.ack()


async def add_and_publish_spin(company, bill_id, phone, cashdesk, publisher):
    gift = await bills.MarketingGift.get_or_create(
        assignment='spin',
        bill_id=bill_id,
    )
    gift = gift[0]
    logger.info(f'gift as spin {gift}')
    if not gift.published:
        spin = {
            'gift_id': gift.id,
            'phone': phone
        }
        if await publisher.publish(
                body=rapidjson.dumps(spin),
                queue_name=f'{company}_{cashdesk}_spin'
        ):
            await gift.save()
            logger.info(f"spin published {phone}")
            return True

    return False


def is_weekend(d=datetime.datetime.today()):
    return d.weekday() > 4

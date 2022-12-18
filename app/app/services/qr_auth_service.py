import inspect

import rapidjson
from sanic.log import logger

from .marketing_db import is_already_assigned
from ..rabbit.rabbit import Rabbit

import os

if os.name == 'nt':
    from app.app.models import bills, qr_auth
    from app.app.shared import tools
else:
    from ..models import bills, qr_auth
    from ..shared import tools


async def process_qr_auth(body: dict, publisher: Rabbit):
    try:
        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                    f'{inspect.stack()[0][3]}: start {body}')

        request_id = body.get('uuid')
        phone = body.get('phone')
        phone = tools.correct_phone(phone)
        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                    f'{inspect.stack()[0][3]}: data {request_id} {phone}')

        if not phone:
            result = {"status": 1, "message": "phone_is _empty"}
            logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {result}')
            return result

        rec = await qr_auth.QrAuth.get(request_id=request_id)
        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                    f'{inspect.stack()[0][3]}: rec.assignment {rec.assignment}')

        if rec.phone:
            result = {"status": 1, "message": "already_scanned"}
            logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {result}')
            return result

        if rec.assignment == 'spin':
            if await is_already_assigned(
                username=rec.username,
                assignment=rec.assignment,
                phone=phone
            ):
                result = {"status": 3, "message": "already_played"}
                logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {result}')
                return result

            rec.phone = phone
            await rec.save()
            marketing_bill = await bills.MarketingBill.get_or_create(
                company=rec.username,
                company_bill_id=request_id,
                phone=phone
            )
            await marketing_bill[0].save()

            if not await add_and_publish_spin(
                company=rec.username,
                bill_id=marketing_bill[0].id,
                phone=phone,
                publisher=publisher
            ):
                result = {"status": 1, "message": "already_scanned"}
                logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {result}')
                return result
            else:
                result = {"status": 0, "message": "Іске сәт!"}
                logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {result}')
                return result
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        result = {"status": 2, "message": "unrecognized"}
        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {result}')
        return result


async def add_and_publish_spin(company, bill_id, phone, publisher):
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
                queue_name=f'{company}_spin'
        ):
            await gift.save()
            logger.info(f"spin published {phone}")
            return True

    return False


import datetime
import inspect
import math

import rapidjson
from sanic.log import logger
from ..models import bills


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


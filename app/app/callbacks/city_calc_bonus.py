import datetime
import inspect
import math

import rapidjson
from sanic.log import logger

from ..rabbit.rabbit import Rabbit
from ..shared.tools import clock_emoji
from ..models import bills

#####################################################################
MIN_PAYMENT = 10000
CASHBACK = 0.15
WEEKENDS_CASHBACK = 0.10
TOKEN_ID = 66
#####################################################################


async def calc_city_bonus(message, publisher: Rabbit):
    try:
        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                    f'{inspect.stack()[0][3]}: start {message.body}')

        bill_dict = rapidjson.loads(message.body)

        bill_id = bill_dict.get('bill_id')
        bill = await bills.MarketingBill.get(id=bill_id)
        company = bill.company
        cashdesk = bill.cashdesk
        phone = bill.phone
        amount = bill.amount
        paytime = bill.paytime

        deal = calc_city_cashback(amount=amount, paytime=paytime)

        if deal:
            public_phone = f"{phone[0:5]}***{phone[-4:]}"
            screen_msg = f"[cyan1]{public_phone}: " \
                         f"[white]Кэшбэк [magenta2]{deal.get('msg')}"

            await add_and_publish_cashback(
                bill_id=bill_id,
                deal=deal,
                screen_msg=screen_msg,
                phone=phone,
                publisher=publisher
            )
            await add_and_publish_spin(
                company=company,
                bill_id=bill_id,
                phone=phone,
                cashdesk=cashdesk,
                publisher=publisher
            )

        await message.ack()
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} {inspect.stack()[0][3]}: {e}')
        await message.ack()
        # await publisher.ttl_publish(
        #     body=rapidjson.dumps(rapidjson.loads(message.body)),
        #     queue_name='aqua_calc_bonus',
        #     minutes=10
        # )


async def add_and_publish_cashback(
        bill_id, deal: dict, screen_msg, phone, publisher
):
    gift = await bills.MarketingGift.get_or_create(
        assignment='cashback',
        bill_id=bill_id,
    )
    gift = gift[0]
    logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                f'{inspect.stack()[0][3]}: gift as cashback {gift}')
    if not gift.published:
        gift.deal = deal
        gift.screen_msg = screen_msg
        await gift.save()
        if await publisher.publish(
                body=rapidjson.dumps({'gift_id': gift.id}),
                queue_name='send_gift'
        ):
            gift.published = True
            await gift.save()
            logger.info(f"cashback published {phone}")
    else:
        logger.info(f"cashback already published {phone}")


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


def is_weekend(d=datetime.datetime.today()):
    return d.weekday() > 4


def calc_city_cashback(amount, paytime):
    cashback_percent = WEEKENDS_CASHBACK if is_weekend(paytime) else CASHBACK
    if amount < MIN_PAYMENT:
        cashback = 1
        # return {}
    else:
        cashback = round(amount * cashback_percent)

    amounts1 = [cashback]
    ids1 = [TOKEN_ID]
    msg = f"🪙ЖарKoin {cashback}={amount}✖" \
          f"{int(cashback_percent * 100)}% " \
          f"🗓{paytime.strftime('%d.%m.%y')}{clock_emoji(paytime)}{paytime.strftime('%H:%M')}"

    deal = {
        'ids1': ids1,
        'amounts1': amounts1,
        'msg': msg
    }
    logger.info(f"calc_aqua_cashback: {deal}")
    return deal
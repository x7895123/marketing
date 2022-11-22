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
TOKEN_ID = 37
TICKET_TOKEN_ID = 59
TICKET_GUEST_COUNT = 2
MIN_GUEST_COUNT = 2

FITNESS_MIN_PAYMENT = 10000
FITNESS_CASHBACK = 0.10
FITNESS_TOKEN_ID = 37
FITNESS_TICKET_TOKEN_ID = 48
FITNESS_ACTION_CASHBACK = 0.3
FITNESS_ACTION_BEGIN_DATE = '2022-09-22'
FITNESS_ACTION_END_DATE = '2022-10-07'


#####################################################################


async def calc_aqua_bonus(message, publisher: Rabbit):
    try:
        logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][2]} '
                    f'{inspect.stack()[0][3]}: start {message.body}')

        bill_dict = rapidjson.loads(message.body)

        bill_id = bill_dict.get('bill_id')
        bill = await bills.MarketingBill.get(id=bill_id)
        company = bill.company
        cashdesk = bill.cashdesk
        phone = bill.phone
        original_bill = bill.original_bill

        idaccount = original_bill.get('idaccount')
        id_fitness_payment = original_bill.get('id_fitness_payment')
        payment = original_bill.get('payment')
        guest_count = original_bill.get('guest_count') or 0
        acc_close_date = original_bill.get('acc_close_date')
        deal = bill.deal
        if not deal:
            if idaccount:
                deal = calc_aqua_cashback(
                    acc_close_date=acc_close_date,
                    payment=payment,
                    guest_count=guest_count)
            elif id_fitness_payment:
                deal = calc_fitness_cashback(
                    acc_close_date=acc_close_date,
                    payment=payment
                )

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
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        await publisher.ttl_publish(
            body=message.body,
            queue_name='aqua_calc_bonus',
            minutes=10
        )


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


def calc_aqua_cashback(acc_close_date, payment, guest_count):
    if payment < MIN_PAYMENT:
        return {}

    t = datetime.datetime.strptime(acc_close_date, '%Y-%m-%d %H:%M:%S')
    cashback_percent = WEEKENDS_CASHBACK if is_weekend(t) else CASHBACK

    cashback = round(payment * cashback_percent)

    tickets_amount = math.trunc(guest_count / TICKET_GUEST_COUNT) \
        if guest_count >= MIN_GUEST_COUNT \
        else 0
    if tickets_amount > 0:
        amounts1 = [cashback, tickets_amount]
        ids1 = [TOKEN_ID, TICKET_TOKEN_ID]
        if tickets_amount == 1:
            ticket_msg = f'{tickets_amount} Билет'
        elif 1 < tickets_amount < 5:
            ticket_msg = f'{tickets_amount} Билета'
        else:
            ticket_msg = f'{tickets_amount} Билетов'
        msg = f"💰АкваКэш+BONUS {cashback}={payment}✖" \
              f"{int(cashback_percent * 100)}% + {ticket_msg} " \
              f"🗓{t.strftime('%d.%m.%y')}{clock_emoji(t)}{t.strftime('%H:%M')}"
    else:
        amounts1 = [cashback]
        ids1 = [TOKEN_ID]
        msg = f"💰АкваКэш {cashback}={payment}✖" \
              f"{int(cashback_percent * 100)}% " \
              f"🗓{t.strftime('%d.%m.%y')}{clock_emoji(t)}{t.strftime('%H:%M')}"

    deal = {
        'ids1': ids1,
        'amounts1': amounts1,
        'msg': msg
    }
    logger.info(f"calc_aqua_cashback: {deal}")
    return deal


def calc_fitness_cashback(acc_close_date, payment):
    if payment < FITNESS_MIN_PAYMENT:
        return {}

    t = datetime.datetime.strptime(acc_close_date, '%Y-%m-%d %H:%M:%S')
    action_begin_date = datetime.datetime.strptime(
        FITNESS_ACTION_BEGIN_DATE, '%Y-%m-%d'
    )
    action_end_date = datetime.datetime.strptime(
        FITNESS_ACTION_END_DATE, '%Y-%m-%d'
    )

    cashback_percent = FITNESS_ACTION_CASHBACK if (
            action_begin_date <= t <= action_end_date
    ) else FITNESS_CASHBACK
    cashback = round(payment * cashback_percent)

    tickets_amount = math.trunc(payment / FITNESS_MIN_PAYMENT)

    amounts1 = [cashback, tickets_amount]
    ids1 = [FITNESS_TOKEN_ID, FITNESS_TICKET_TOKEN_ID]

    if tickets_amount == 1:
        ticket_msg = f'{tickets_amount} Билет'
    elif 1 < tickets_amount < 5:
        ticket_msg = f'{tickets_amount} Билета'
    else:
        ticket_msg = f'{tickets_amount} Билетов'
    msg = f"💰АкваКэш+BONUS {cashback}={payment}✖" \
          f"{int(cashback_percent * 100)}% + {ticket_msg} " \
          f"🗓{t.strftime('%d.%m.%y')}{clock_emoji(t)}{t.strftime('%H:%M')}"

    deal = {
        'ids1': ids1,
        'amounts1': amounts1,
        'msg': msg
    }
    logger.info(f"calc_aqua_cashback: {deal}")
    return deal

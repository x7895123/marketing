import datetime
import inspect
import math

import rapidjson
from sanic.log import logger

from app.rabbit.rabbit import Rabbit
from app.services.aqua_api import dml_request
from app.services.dostyq_marketing import send_gift
from app.services.marketing_db import update_cashback
from app.shared.tools import clock_emoji

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


def calc_aqua_bonus(message, publisher: Rabbit):
    logger.debug(f"Received {message.body}")
    bill = rapidjson.loads(message.body)

    # index, idaccount, id_fitness_payment, summa, acc_close_date, phone, address, task = payment.values()
    source = bill.get('source')
    bill_id = bill.get('bill_id')
    phone = bill.get('phone')
    task = bill.get('task')

    original_bill = bill.get('original_bill')
    index = original_bill.get('index')

    if not phone:
        message.ack()
        return

    if source == 'cashback':
        id_cashback = bill.get('id_cashback')
        if task:
            gift = {
                "phone": phone,
                "bill_id": bill_id,
                "delay": 0,
                **task
            }
            if await send_gift(gift) > 0:
                update_cashback(id_cashback, {"sent_ts": datetime.datetime.now()})
                sql = f"update ud_cashback set sent_date = cast('now' as date) where id = {index}"
                dml_request(sql)
                publisher.publish(message.body, 'aqua_spin')
                logger.info(f"spin published {phone}")
            else:
                publisher.ttl_publish(message.body, 'aqua_calc_bonus', minutes=10)

            message.ack()
            return

        idaccount = original_bill.get('idaccount')
        id_fitness_payment = original_bill.get('id_fitness_payment')
        payment = original_bill.get('payment')
        guest_count = original_bill.get('guest_count', 0)
        acc_close_date = original_bill.get('acc_close_date')

        if idaccount:
            task = calc_aqua_cashback(
                acc_close_date=acc_close_date,
                payment=payment,
                guest_count=guest_count)
        elif id_fitness_payment:
            task = calc_fitness_cashback(acc_close_date, payment)

        if task:
            gift = {
                "phone": phone,
                "bill_id": bill_id,
                "delay": 0,
                **task
            }
            sql = f"update ud_cashback set task = '{rapidjson.dumps(task)}' where id = {index}"
            dml_request(sql)

            if await send_gift(gift) > 0:
                update_cashback(id_cashback, {"sent_ts": datetime.datetime.now()})
                sql = f"update ud_cashback set sent_date = cast('now' as date) where id = {index}"
                dml_request(sql)
                publisher.publish(message.body, 'aqua_spin')
                logger.info(f"spin published {phone}")
            else:
                bill.update("task", task)
                publisher.ttl_publish(rapidjson.dumps(bill), 'aqua_calc_bonus', minutes=10)
        else:
            update_cashback(id_cashback, {"sent_ts": datetime.datetime.now(), "error_message": "no bonus"})
            sql = f"update ud_cashback set sent_date = cast('now' as date), description = 'no bonus' where id = {index}"
            dml_request(sql)

        message.ack()
        return

    sql = f"update ud_cashback set sent_date = cast('now' as date), description = 'no bonus' where id = {index}"
    dml_request(sql)
    message.ack()


def update_send_gift(bill_no, index, phone, delay, task: dict):
    """
    gift = {
          "ids1": [4, 51],
          "amounts1": [1000, 2],
          "phone": "+77010000000",
          "msg": "🥳 Құттықтаймыз! 恭喜!",
          "bill_id": "z7895123",
          "delay": 15,
          "send_date": "2022-11-09 12:06:27 +6"
        }

    send_gift = 0 - отправил
    send_gift = 1 - уже было отправлено
    send_gift = -1 - ошибка отправки
    """
    # Save to task field calc bonus
    sql = f"update ud_cashback set task = '{rapidjson.dumps(task)}' where id = {index}"
    dml_request(sql)

    payload = {
        "phone": phone,
        "bill_id": bill_no,
        "delay": int(delay)
    }

    result = send_gift(payload)
    logger.info(f"send_gift result: {result}")
    if result >= 0:
        if index == bill_id:
            sql = f"update ud_cashback set sent_date = cast('now' as date) where id = {index}"
        else:
            sql = f"update ud_cashback set present_date = cast('now' as date) where id = {index}"
        dml_request(sql)
    else:
        gift.update({"task": task})
        body = rapidjson.dumps(gift)
        publisher.publish(body=body, queue_name='calc_aqua_bonus', minutes=40)
    return result == 0


def is_weekend(d=datetime.datetime.today()):
    return d.weekday() > 4


def calc_aqua_cashback(acc_close_date, payment, guest_count):
    if payment < MIN_PAYMENT:
        return {}

    t = datetime.datetime.strptime(acc_close_date, '%d.%m.%y %H:%M:%S')
    cashback_percent = WEEKENDS_CASHBACK if is_weekend(t) else CASHBACK

    cashback = round(payment * cashback_percent)

    tickets_amount = math.trunc(guest_count / TICKET_GUEST_COUNT) if guest_count >= MIN_GUEST_COUNT else 0
    if tickets_amount > 0:
        amounts1 = [cashback, tickets_amount]
        ids1 = [TOKEN_ID, TICKET_TOKEN_ID]
        if tickets_amount == 1:
            ticket_msg = f'{tickets_amount} Билет'
        elif 1 < tickets_amount < 5:
            ticket_msg = f'{tickets_amount} Билета'
        else:
            ticket_msg = f'{tickets_amount} Билетов'
        msg = f"💰АкваКэш+BONUS {cashback}={payment}✖{int(cashback_percent * 100)}% + {ticket_msg} 🗓{t.strftime('%d.%m.%y')}{clock_emoji(t)}{t.strftime('%H:%M')}"
    else:
        amounts1 = [cashback]
        ids1 = [TOKEN_ID]
        msg = f"💰АкваКэш {cashback}={payment}✖{int(cashback_percent * 100)}% 🗓{t.strftime('%d.%m.%y')}{clock_emoji(t)}{t.strftime('%H:%M')}"

    task = {
        'ids': ids1,
        'amounts1': amounts1,
        'msg': msg
    }
    logger.info(f"calc_aqua_cashback: {task}")
    return task


def calc_fitness_cashback(acc_close_date, payment):
    if payment < FITNESS_MIN_PAYMENT:
        return {}

    t = datetime.datetime.strptime(acc_close_date, '%d.%m.%y %H:%M:%S')
    action_begin_date = datetime.datetime.strptime(FITNESS_ACTION_BEGIN_DATE, '%Y-%m-%d')
    action_end_date = datetime.datetime.strptime(FITNESS_ACTION_END_DATE, '%Y-%m-%d')

    cashback_percent = FITNESS_ACTION_CASHBACK if (action_begin_date <= t <= action_end_date) else FITNESS_CASHBACK
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
    msg = f"💰АкваКэш+BONUS {cashback}={payment}✖{int(cashback_percent * 100)}% + {ticket_msg} 🗓{t.strftime('%d.%m.%y')}{clock_emoji(t)}{t.strftime('%H:%M')}"

    task = {
        'ids': ids1,
        'amounts1': amounts1,
        'msg': msg
    }
    logger.info(f"calc_aqua_cashback: {task}")
    return task


def calc_gift(index, phone, token_id, summa):
    cashback = int(summa)
    amounts1 = [cashback]
    ids1 = [token_id]
    msg = f"Тамаша жетістіктер үшін 🔹 За отличные  успехи"
    bill_id = index
    delay = 0
    logger.info(f"ids1: {ids1}, amounts1: {amounts1}, phone: {phone}, msg: {msg}, bill_id: {bill_id}, delay: {delay}")
    return ids1, amounts1, phone, msg, bill_id, delay

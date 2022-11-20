import inspect
from ast import literal_eval

from tortoise import Tortoise
import rapidjson
import datetime
from sanic.log import logger

from app.models import bills
from app.shared import tools


def d():
    print('hi')


async def add_bill(bill: dict, company):
    try:
        phone = str(bill.get('phone'))
        if not phone:
            logger.info(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: phone is not defined')
            return {'error': 'phone is not defined'}
        phone = tools.correct_phone(phone)
        company_bill_id = str(bill.get('company_bill_id'))
        if not company_bill_id:
            return {'error': 'company_bill_id is not defined'}
        company_bill_id = f"{company}-{company_bill_id}"
        cashdesk = bill.get('cashdesk', company)
        paytime = bill.get('paytime', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        amount = bill.get('amount')
        amount = int(amount) if amount else 0
        task = bill.get('task', {})

        marketing_bill = await bills.MarketingBill.get_or_create(
            company=company,
            cashdesk=cashdesk,
            company_bill_id=company_bill_id,
            phone=phone,
            amount=amount,
            paytime=paytime,
            original_bill=bill,
            task=task
        )
        # logger.info(marketing_bill[0])
        logger.info(marketing_bill[0].id)
        marketing_gift = await bills.MarketingGift.get_or_create(
            phone=phone,
            assignment='cashback',
            bill_id=marketing_bill[0].id
        )

        return {
            "bill_id": marketing_bill[0].id,
            "company": company,
            "cashdesk": cashdesk,
            "phone": phone,
            "amount": amount,
            "paytime": paytime,
            "original_bill": bill,
            "task": task,
            'gift_id': marketing_gift[0].id,
            "assignment": "cashback",
            'published': marketing_gift[0].published,
        }
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return {"error": e}


async def update_from_dict_cashback(id_cashback, data: dict):
    try:
        marketing_cashback = await bills.MarketingCashback.get(id=id_cashback)
        await marketing_cashback.update_from_dict(data)
        await marketing_cashback.save()
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return {"error": e}


# async def update_cashback(id_cashback, field, value):
#     try:
#         marketing_cashback = await bills.MarketingCashback.get(id=id_cashback)
#         await bills.MarketingCashback.filter(id=id_cashback).update('field'="Updated name")
#         await marketing_cashback.save()
#     except Exception as e:
#         logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
#         return {"error": e}


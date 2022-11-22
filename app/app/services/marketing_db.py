import inspect
import datetime
from sanic.log import logger

from ..models import bills
from ..shared import tools


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
        deal = bill.get('task', {})

        marketing_bill = await bills.MarketingBill.get_or_create(
            company=company,
            cashdesk=cashdesk,
            company_bill_id=company_bill_id,
            phone=phone,
            amount=amount,
            paytime=paytime,
            original_bill=bill,
            deal=deal
        )
        await marketing_bill[0].save()
        logger.info(f"bill saved: {marketing_bill[0]}")
        return marketing_bill[0]
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


async def add_gift(bill_id, assignment):
    try:
        marketing_gift = await bills.MarketingGift.get_or_create(
            assignment=assignment,
            bill_id=bill_id,
        )
        return marketing_gift
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None

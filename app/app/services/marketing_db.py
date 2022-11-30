import inspect
import datetime
import os

import tortoise

from sanic.log import logger

if os.name == 'nt':
    from app.app.models import bills, users
    from app.app.shared import tools, settings
else:
    from ..models import bills, users
    from ..shared import tools


def d():
    print('hi')


async def add_bill(bill: dict, company):
    try:
        phone = str(bill.get('phone'))
        if not phone:
            logger.info(
                f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: phone is not defined')
            return {'error': 'phone is not defined'}
        phone = tools.correct_phone(phone)
        company_bill_id = str(bill.get('company_bill_id'))
        if not company_bill_id:
            return {'error': 'company_bill_id is not defined'}
        company_bill_id = f"{company}-{company_bill_id}"
        cashdesk = bill.get('cashdesk', company)
        paytime = bill.get('paytime', datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"))
        amount = bill.get('amount')
        amount = int(amount) if amount else 0
        deal = bill.get('deal', {})

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


async def add_user(name, password_hash, company, cashdesk):
    try:
        user = await users.Users.get_or_create(
            name=name,
            password_hash=password_hash,
            company=company,
            cashdesk=cashdesk,
        )
        await user[0].save()
        return user
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


async def get_users():
    try:
        result = await users.Users.all().exclude(
            name__in=['puppeteer', 'guest']
        ).values("name")
        print([x.get('name') for x in result])
        return [x.get('name') for x in result]
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


async def get_password_hash(username):
    try:
        result = await users.Users.filter(name=username).values("password_hash")
        print(result[0].get('password_hash') if result else b"")
        return result[0].get('password_hash') if result else b""
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


if __name__ == '__main__':
    from app.app.routes.login import users as us

    config = {
        'connections': {
            # Dict format for connection
            'arena': {
                'engine': 'tortoise.backends.asyncpg',
                'credentials': {
                    'host': '192.168.90.221',
                    'port': '6000',
                    'user': 'arena',
                    'password': 'arenajkfmg7pdo5',
                    'database': 'arena',
                }
            },
        },
        'apps': {
            'models': {
                'models': ['app.app.models.bills', 'app.app.models.users',
                           "aerich.models"],
                # If no default_connection specified, defaults to 'default'
                'default_connection': 'arena',
            }
        }
    }

    tortoise.run_async(tortoise.Tortoise.init(config=config))
    tortoise.run_async(tortoise.Tortoise.generate_schemas())
    # for uname, upassword_hash in us.items():
    #     tortoise.run_async(add_user(name=uname, password_hash=upassword_hash, company='aqua', cashdesk='aqua'))
    tortoise.run_async(
        get_password_hash('arena1')
    )

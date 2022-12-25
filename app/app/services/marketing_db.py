import inspect
import datetime
import os

import uuid

import tortoise

from sanic.log import logger
from base64 import b64encode

from tortoise.expressions import Q

if os.name == 'nt':
    from app.app.models import bills, users, qr_auth
    from app.app.shared import tools
else:
    from ..models import bills, users, qr_auth
    from ..shared import tools


def d():
    print('hi')


async def add_qr_auth(username, assignment):
    try:
        request_id = str(uuid.uuid4())
        rec = await qr_auth.QrAuth.get_or_create(
            username=username,
            request_id=request_id,
            assignment=assignment
        )
        await rec[0].save()
        logger.info(f"qr_auth saved: {rec[0]}")
        return request_id
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


async def add_bill(bill: dict, username):
    try:

        user = await users.Users.get(name=username)
        company = user.company
        user_cashdesk = user.cashdesk

        phone = str(bill.get('phone'))
        phone = tools.correct_phone(phone)
        if not phone:
            logger.info(
                f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: phone is not defined')
            return {'error': 'phone is not defined'}
        company_bill_id = str(bill.get('company_bill_id'))
        if not company_bill_id:
            return {'error': 'company_bill_id is not defined'}
        company_bill_id = f"{company}-{company_bill_id}"
        cashdesk = bill.get('cashdesk', user_cashdesk)
        paytime = bill.get('paytime', datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"))
        amount = bill.get('amount')
        amount = int(amount) if amount else 0
        deal = bill.get('deal', {})

        marketing_bill = await bills.MarketingBill.get_or_create(
            username=username,
            company=company,
            cashdesk=cashdesk,
            company_bill_id=company_bill_id,
            phone=phone,
            amount=amount,
            paytime=paytime,
            original_bill=bill,
            deal=deal,
            users_id=user.id
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


async def add_user(name, password, company, cashdesk):
    try:
        user = await users.Users.get_or_create(
            name=name,
            password=password,
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
        logger.info([x.get('name') for x in result])
        return [x.get('name') for x in result]
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


async def get_password_hash(username):
    try:
        result = await users.Users.filter(name=username).values("password_hash")
        logger.info(result[0].get('password_hash').encode('utf-8') if result else b"")
        return result[0].get('password_hash').encode('utf-8') if result else b""
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


async def check_user(username, password):
    try:
        result = await users.Users.exists(
            Q(name=username) & Q(password=password)
        )
        print(result)
        return result
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


async def get_user_company(username):
    try:
        result = await users.Users.filter(name=username).values("company")
        logger.info(result[0].get('company') if result else "")
        return result[0].get('company') if result else ""
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


async def get_user(username) -> users.Users:
    result = await users.Users.get(name=username)
    return result
    # try:
    #     result = await users.Users.get(name=username)
    #     return result
    # except Exception as e:
    #     logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
    #     return None


async def is_already_assigned(username, assignment, phone):
    try:
        if phone in ('+77010000864', '+77014123999'):
            return False

        result = await qr_auth.QrAuth.exists(
            Q(username=username) & Q(assignment=assignment) & Q(phone=phone)
        )
        print(result)
        return result
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return None


async def assign_user_code(username, code):
    try:
        user = await users.Users.get(name=username)
        user.code = code
        await user.save()
        return True
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return False


async def get_authorization(code):
    try:
        user = await users.Users.get(code=code)
        token = b64encode(f"{user.name}:{user.password}".encode('utf-8')).decode("ascii")
        print(f"Basic {token}")
        return f"Basic {token}"
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return ""


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
                'models': ['app.app.models.bills', 'app.app.models.users', 'app.app.models.qr_auth',
                           "aerich.models"],
                # If no default_connection specified, defaults to 'default'
                'default_connection': 'arena',
            }
        }
    }

    tortoise.run_async(tortoise.Tortoise.init(config=config))
    tortoise.run_async(tortoise.Tortoise.generate_schemas())
    tortoise.run_async(is_already_assigned(username='city', assignment='spin', phone='+77010000864'))


    # tortoise.run_async(
    #     add_user(
    #         name="city",
    #         password="cityJkfmg7pdo5",
    #         company='aqua',
    #         cashdesk='city'
    #     )
    # )

    # for uname, upassword in us.items():
    #     tortoise.run_async(
    #         add_user(
    #             name=uname,
    #             password=upassword,
    #             company='aqua',
    #             cashdesk='aqua'
    #         )
    #     )
    # tortoise.run_async(
    #     assign_user_code(username="aqua", code="123")
    # )
    # tortoise.run_async(
    #     get_authorization(code="123")
    # )
    # tortoise.run_async(
    #     get_authorization(code="321")
    # )


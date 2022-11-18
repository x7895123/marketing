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
        bill_no = str(bill.get('bill_no'))
        if bill_no is None:
            return {'error': 'Bill № is not defined'}
        bill_no = f"{company}-{bill_no}"
        cashdesk = bill.get('cashdesk', company)
        paytime = bill.get('paytime', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        amount = bill.get('amount')
        amount = int(amount) if amount else 0
        task = bill.get('task', {})

        marketing_bill = await bills.MarketingBill.get_or_create(
            company=company,
            cashdesk=cashdesk,
            bill_no=bill_no,
            phone=phone,
            amount=amount,
            paytime=paytime,
            bill=bill,
            task=task
        )
        logger.info(marketing_bill[0])
        marketing_cashback = await bills.MarketingCashback.get_or_create(
            phone=phone,
            id_bill=marketing_bill[0]
        )
        logger.info(marketing_cashback[0])
        return marketing_bill, marketing_cashback


        # sql = f"""
        #         insert into public.marketing_bill (company,cashdesk,phone,company_bill_no,paytime,amount,bill,task)
        #         values('{company}','{cashdesk}','{phone}','{bill_no}','{paytime}',{amount},'{rapidjson.dumps(bill)}','{task}')
        #         ON CONFLICT ON CONSTRAINT marketing_bill_un DO NOTHING
        #         RETURNING id
        #     """
        # logger.debug(sql)
        # conn = Tortoise.get_connection("arena")
        # result = await conn.execute_query_dict(sql)
        # logger.debug(f"marketing add_bill: {result}")
        # if result:
        #     id_marketing_bill = int(result[0].get('id'))
        #     logger.debug(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: id_marketing_bill {id_marketing_bill}")
        #     body = {
        #         'company': company,
        #         'cashdesk': cashdesk,
        #         'phone': phone,
        #         'bill_no': bill_no,
        #         'paytime': paytime,
        #         'amount': amount,
        #         'bill': bill,
        #         'task': task,
        #         'id_marketing_bill': id_marketing_bill
        #     }
        #     logger.debug(
        #         f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: body {body}")
        #     return {"body": body}
        # else:
        #     logger.debug(
        #         f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: Company bill_no {bill_no} already exists"
        #     )
        #
        #     return {"warning": f"Company bill_no {bill_no} already exists"}
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return {"error": e}


async def get_cashback(bill_no):
    try:
        sql = f"""
            select
                c.id id_marketing_bill,
                c.id_bill, c.phone, c.create_ts, c.sent_ts, c.expiration_ts, c.deal, c.deal_status, c.error_message, c.recipient_address, c.contract_address from public.marketing_cashback c
            where c.bill_no = 
            """
        logger.debug(sql)
        conn = Tortoise.get_connection("arena")
        result = await conn.execute_query_dict(sql)
        logger.debug(f"marketing add_bill: {result}")
        if result:
            return

    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return {"error": e}


async def update_bill(id_marketing_bill, status, message):
    try:
        sql = f"""
                update public.marketing_bill 
                set status = '{status}', message = '{message}' 
                where id = {id_marketing_bill}
            """
        logger.debug(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {sql}')
        conn = Tortoise.get_connection("marketing")
        result = await conn.execute_query(sql)
        logger.debug(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {result}')
        return True
    except Exception as e:
        logger.error(f"{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}")
        return False


async def get_company_mnemonic(id_company):
    try:

        sql = f"select mnemonic from public.marketing_company where id = '{id_company}'"
        # print(sql)
        conn = Tortoise.get_connection("marketing")
        result = await conn.execute_query_dict(sql)
        # print(result)
        if result:
            mnemonic = result[0].get('mnemonic')
            logger.info(f"get_company_mnemonic: {id_company} - {mnemonic}")
            return mnemonic
        else:
            logger.info(f"get_company_mnemonic: {id_company} - not found")
            return None
    except Exception as e:
        logger.error(f"get_company_mnemonic: {e}")
        return None


async def subscription_exists(id_company, phone):
    try:
        conn = Tortoise.get_connection("marketing")
        sql = f"""
                select count(*) 
                from public.marketing_subscriptions s 
                where s.id_company = '{id_company}' and phone = '{phone}'
            """
        logger.debug(f"marketing check_subscription_exists sql: {sql}")
        result = await conn.execute_query_dict(sql)
        logger.debug(f"marketing check_subscription_exists: {result}")
        if result:
            if int(result[0].get('count')) == 0:
                return False
            else:
                return True
    except Exception as e:
        logger.error(f"marketing_db check_subscription_exists: {e}")
        return None


async def add_subscription(id_company, phone, url):
    try:
        conn = Tortoise.get_connection("marketing")
        sql = f"""
                insert into public.marketing_subscriptions(id_company, phone, url) 
                values ('{id_company}', '{phone}', '{url}')
            """
        logger.debug(f"marketing add_subscription sql: {sql}")
        result = await conn.execute_query(sql)
        logger.debug(f"marketing add_subscription: {result}")
        return True
    except Exception as e:
        logger.error(f"marketing add_subscription: {e}")
        return False


async def update_subscription_state(id_company, phone, status, message):
    try:
        conn = Tortoise.get_connection("marketing")
        sql = f"""
                update public.marketing_subscriptions 
                set notification_ts = current_timestamp, status = '{status}', message = '{message}'
                where id_company = '{id_company}' and phone = '{phone}' 
            """
        logger.debug(f"marketing update_subscription_state sql: {sql}")
        result = await conn.execute_query(sql)
        logger.debug(f"marketing update_subscription_state: {result}")
        return True
    except Exception as e:
        logger.error(f"marketing update_subscription_state: {e}")
        return False


async def create_deferred_task(id_company, phone, task: dict, bill_id, source):
    try:
        conn = Tortoise.get_connection("marketing")
        if bill_id:
            sql = f"""
                        insert into public.marketing_deferred_task(id_company, phone, task, bill_id, source) 
                        values ('{id_company}', '{phone}', '{rapidjson.dumps(task)}', '{bill_id}', '{source}')
                        ON CONFLICT ON CONSTRAINT marketing_deferred_task_un_bill DO NOTHING
                        RETURNING id
                """
        else:
            sql = f"""
                        insert into public.marketing_deferred_task(id_company, phone, task) 
                        values ('{id_company}', '{phone}', '{rapidjson.dumps(task)}')
                        ON CONFLICT ON CONSTRAINT marketing_deferred_task_un_bill DO NOTHING
                        RETURNING id
                """

        logger.debug(f"marketing create_deferred_task sql: {sql}")
        result = await conn.execute_query_dict(sql)
        if result:
            logger.debug(f"marketing create_deferred_task: {result}")
            id_task = result[0].get('id')
            return {"id_task": id_task}
        else:
            return await self.get_contract_address_from_task(bill_id)
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        return {"error": e}


async def get_contract_address_from_task(bill_id):
    conn = Tortoise.get_connection("marketing")
    sql = f"""
                    select id, contract_address from public.marketing_deferred_task 
                    where bill_id = '{bill_id}' and deal_status = 'ERROR'
                """
    result = await conn.execute_query_dict(sql)
    if result:
        id_task = result[0].get('id')
        contract_address = result[0].get('contract_address')
        return {"id_task": id_task, "contract_address": contract_address}
    else:
        logger.debug(f"marketing db get_contract_address_from_task : {bill_id} not found")
        id_task = -1
        return {"id_task": id_task}


async def get_deferred_tasks(id_company, phone):
    try:
        conn = Tortoise.get_connection("marketing")
        sql = f"""
            select
                id,
                id_company, 
                phone,  
                task ->> 'msg' msg,
                task ->> 'bill_id' bill_id,	
                replace(replace(task ->> 'ids1', '[', '{{'), ']', '}}')::int[] ids1,
                replace(replace(task ->> 'amounts1', '[', '{{'), ']', '}}')::int[] amounts1,
                GREATEST(abs((task ->> 'delay')::int) - (Extract(epoch FROM (now() - create_ts))*1000), 0)::int delay                        
            from public.marketing_deferred_task
            where phone = '{phone}' and id_company = '{id_company}' and sent_date is null
            """
        logger.debug(f"marketing get_deferred_tasks sql: {sql}")
        result = await conn.execute_query_dict(sql)
        logger.debug(f"marketing get_deferred_task: {result}")
        return result
    except Exception as e:
        logger.error(f"marketing get_deferred_task: {e}")
        return []


async def update_recipient_address(id_task, recipient_address):
    try:
        conn = Tortoise.get_connection("marketing")
        sql = f"""
                update public.marketing_deferred_task
                set
                    recipient_address = '{recipient_address}'
                 where id = {id_task}    
            """
        logger.debug(f"marketing update_recipient_address sql: {sql}")
        result = await conn.execute_query(sql)
        logger.debug(f"marketing update_recipient_address result: {result}")
        return True
    except Exception as e:
        logger.error(f"marketing update_recipient_address: {e}")
        return False


async def set_sent_state(id_task, recipient_address, contract_address, deal_status, error_message):
    try:
        conn = Tortoise.get_connection("marketing")
        set_sent_date = 'sent_date = current_timestamp,' if contract_address else ''
        set_recipient_address = f"recipient_address = '{recipient_address}'," if recipient_address else ''
        set_contract_address = f"contract_address = '{contract_address}'," if contract_address else ''
        sql = f"""
                update public.marketing_deferred_task
                set
                    {set_sent_date}
                    {set_recipient_address}
                    {set_contract_address}
                    deal_status = '{deal_status}',
                    error_message = '{error_message}'
                 where id = {id_task}    
            """
        logger.debug(f"marketing set_sent_state sql: {sql}")
        result = await conn.execute_query(sql)
        logger.debug(f"marketing set_sent_state result: {result}")
        return True
    except Exception as e:
        logger.error(f"marketing set_sent_state: {e}")
        return False

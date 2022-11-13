import inspect

import bcrypt
from tortoise import Tortoise


class Db:

    def __init__(self, logger):
        self.logger = logger
        # self.conn = Tortoise.get_connection("market")

    async def verify_password(self, username, password):
        # valid = synchronize_async_helper(app.ctx.iou_db.check_user(username, password))
        # valid = asyncio.run(app.ctx.iou_db.check_user(username, password))
        # app.ctx.logger.debug("verify_password {username}, {password}")
        valid = await self.check_user(username, password)
        self.logger.info(f"basic_auth verify_password - {valid}")
        # valid = True
        if valid:
            return True

        self.logger.error(f"verify_password - username or password do not match")
        return False

    async def verify_token(self, token):
        try:
            self.logger.info(f"verify_token - {token}")
            return await self.check_access_token(token)
        except Exception as e:
            self.logger.error(f"verify_token - {e}")
            return False

    async def check_access_token(self, access_token):
        conn = Tortoise.get_connection("market")
        sql = f"""
            select count(*)
            from public.sys_access_token 
            where token_value = '{access_token}' and current_timestamp < expiry
        """
        self.logger.info(f"sql: {sql}")
        result = await conn.execute_query_dict(sql)
        if result[0].get('count') > 0:
            self.logger.info(f"check_access_token: {access_token} is valid")
            return True
        else:
            self.logger.info(f"check_access_token: {access_token} is invalid")
            return False

    async def get_access_token(self, username):
        try:
            sql = (f"""
                select t.token_value 
                from public.sys_access_token t
                where t.user_login = '{username}' and Extract(epoch FROM (expiry - current_timestamp))/3600 > 10
                order by create_ts desc
                limit 1
            """)
            self.logger.debug(f"get_access_token sql: {sql}")
            conn = Tortoise.get_connection("market")
            self.logger.debug(f"get_access_token: connected")
            if result := await conn.execute_query_dict(sql):
                self.logger.debug(f"get_access_token result: {result}")
                token = result[0].get('token_value')
                self.logger.debug(f"get_access_token: {token}")
                if token:
                    return token
                else:
                    return ""
            else:
                return ""
        except Exception as e:
            self.logger.error(f"get_access_token: {e}")
            return ""

    async def check_user(self, username, password):
        try:
            byte_password = password.encode('utf-8')
            # salt = b'$2a$10$N22mPS.aO0E02rQ1LBEBye'
            # password_hash = bcrypt.hashpw(byte_password, salt).decode("utf-8")
            # self.logger.info(f"check_user: password_hash - {password_hash}")
            # print(password_hash)
            # print('connected')
            sql = f"""
                select c.id as "id", c.legal_name as "name", u.password as "password" 
                from public.sec_user u
                    join public.marketcore_company_user_link cu on cu.user_id = u.id
                    join public.marketcore_company c on c.id = cu.company_id 
                where login = '{username}'
            """
            print(sql)
            conn = Tortoise.get_connection("market")
            result = await conn.execute_query_dict(sql)
            print(result)
            if result:
                self.logger.info(f"check_user: {username} is valid")
                hashed_password = result[0].get('password')
                hashed_password = hashed_password.encode('utf-8')
                if bcrypt.checkpw(byte_password, hashed_password):
                    company_id = result[0].get('id')
                    company_name = result[0].get('name')
                    sql = f"insert into public.marketing_company (id, name) " \
                          f"values ('{company_id}', '{company_name}') " \
                          f"on conflict (id) DO NOTHING"
                    print(sql)
                    conn = Tortoise.get_connection("marketing")
                    await conn.execute_query(sql)
                    return company_id
                else:
                    self.logger.info(f"check_user. password for {username} is invalid")
                    return None
            else:
                self.logger.info(f"check_user: {username} is invalid")
                return None
        except Exception as e:
            self.logger.error(f"check_user: {e}")
            return None

    async def get_id_company_by_token(self, token):
        try:
            if str(token).startswith("Basic"):
                self.logger.debug(f"get_id_company by token: {token}. Token from Basic Auth")
                return None

            sql = f"""
                select c.id as "id"
                from public.sys_access_token t
                    join public.sec_user u on u.login = t.user_login  
                    join public.marketcore_company_user_link cu on cu.user_id = u.id
                    join public.marketcore_company c on c.id = cu.company_id 
                where t.token_value = '{token}'
            """
            # print(sql)
            conn = Tortoise.get_connection("market")
            result = await conn.execute_query_dict(sql)
            # print(result)
            if result:
                id_company = result[0].get('id')
                self.logger.info(f"get_id_company by token: {token} - {id_company}")
                return id_company
            else:
                self.logger.info(f"get_id_company by token: {token} - not found")
                return None
        except Exception as e:
            self.logger.error(f"check_user: {e}")
            return None

    async def get_id_company(self, request):
        try:
            if token := request.token:
                if str(token).startswith("Basic"):
                    self.logger.debug(f"get_id_company by token: {token}. Token from Basic Auth")
                    username = request.credentials._username
                    sql = f"""
                        select c.id as "id"
                        from public.sec_user u
                            join public.marketcore_company_user_link cu on cu.user_id = u.id
                            join public.marketcore_company c on c.id = cu.company_id
                        where u.login = '{username}'
                    """
                    # print(sql)
                    conn = Tortoise.get_connection("market")
                    result = await conn.execute_query_dict(sql)
                    # print(result)
                    if result:
                        id_company = result[0].get('id')
                        self.logger.info(f"get_id_company by basic token: {token} - {id_company}")
                        return id_company
                    else:
                        self.logger.info(f"get_id_company by basic token: {token} - not found")
                        return None
                else:
                    sql = f"""
                        select c.id as "id"
                        from public.sys_access_token t
                            join public.sec_user u on u.login = t.user_login
                            join public.marketcore_company_user_link cu on cu.user_id = u.id
                            join public.marketcore_company c on c.id = cu.company_id
                        where t.token_value = '{token}'
                    """
                    # print(sql)
                    conn = Tortoise.get_connection("market")
                    result = await conn.execute_query_dict(sql)
                    # print(result)
                    if result:
                        id_company = result[0].get('id')
                        self.logger.info(f"get_id_company by token: {token} - {id_company}")
                        return id_company
                    else:
                        self.logger.info(f"get_id_company by token: {token} - not found")
                        return None
            else:
                return None
        except Exception as e:
            self.logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
            return None

    async def get_transaction_status(self, contract_address):
        try:
            sql = f"""
                select deal_status, error_message 
                from public.marketcore_deal 
                where upper(contract_address) = upper('{contract_address}')
            """
            self.logger.debug(f"get_transaction_status slq: {sql}")
            conn = Tortoise.get_connection("market")
            result = await conn.execute_query_dict(sql)
            self.logger.debug(f"get_transaction_status result: {result}")
            if result:
                self.logger.debug(f"get_transaction_status: {result[0]}")
                return result[0]
            else:
                self.logger.error(f"get_transaction_status: transaction not found")
                return None
        except Exception as e:
            self.logger.error(f"get_transaction_status: {e}")
            return None

    async def get_transaction_status_by_bill_id(self, bill_id, id_company, phone):
        try:
            phone = str(phone).replace('+', '')
            sql = f"""
                with
                    deal_detail as (
                        select p.phone, p.blockchain , t."name", dt.token_id, dt.amount, d.create_ts, d.update_ts, d.deal_type, d.deal_status, d.error_message, d."comment"
                        from public.marketcore_deal d
                            join public.marketcore_deal_part dp on dp.deal_id = d.id
                            join marketcore_profile p on p.blockchain = dp.participant 
                            left join public.marketcore_deal_token dt on dt.deal_part_id = dp.id 
                            left join public.marketcore_token t on t.id = dt.token_id
                        where d.deal_client_id = '{bill_id}'
                    ),
                    cashier_info as (
                        select d.deal_client_id, dp.participant, p.phone 
                            from public.marketcore_deal d
                                join public.marketcore_deal_part dp on dp.deal_id = d.id
                                join marketcore_profile p on p.blockchain = dp.participant
                            where 
                                d.deal_client_id = '{bill_id}' and
                                dp.participant in (
                                    select e.profile_blockchain 
                                    from public.marketcore_employee e
                                    where e.company_id = '{id_company}'
                                )
                            limit 1
                    ), 
                    deal_parts as (
                        select dp.participant, p.phone 
                            from public.marketcore_deal d
                                join public.marketcore_deal_part dp on dp.deal_id = d.id
                                join marketcore_profile p on p.blockchain = dp.participant				
                            where 
                                d.deal_client_id = '{bill_id}'
                    )
                select
                    case
                        when dd.blockchain in (select participant from cashier_info) then '-' else '+' 
                    end operation,
                    case
                        when ('{phone}' in (select phone from deal_parts) or dd.phone in (select phone from cashier_info)) then dd.phone else 'secured' 
                    end phone,
                    dd.name,
                    dd.token_id,
                    dd.amount,
                    dd.create_ts, 
                    dd.update_ts, 
                    dd.deal_type, 
                    dd.deal_status, 
                    dd.error_message, 
                    dd."comment"	
                from deal_detail dd
                where exists (select * from cashier_info)
            """


            # deal_info
            sql = f"""
                select
                    d.contract_address, 
                    to_char(d.create_ts,'YYYY-MM-DD HH24:MI:SS') create_ts, 
                    to_char(d.update_ts,'YYYY-MM-DD HH24:MI:SS') update_ts, 
                    d.provider, 
                    d.deal_type, 
                    d.deal_status, 
                    d.error_message, 
                    d."comment",
                    dp.participant cashier_blockchain, 
                    p.phone cashier_phone, 
                    e.internal_name cashier_name, 
                    e.is_active	cashier_is_active
                from public.marketcore_deal d
                    join public.marketcore_deal_part dp on dp.deal_id = d.id 
                    join public.marketcore_profile p on p.blockchain = dp.participant
                    join public.marketcore_employee e on e.profile_blockchain = dp.participant 
                where
                  d.deal_client_id = '{bill_id}' and
                  dp.participant in (
                    select e.profile_blockchain 
                    from public.marketcore_employee e
                    where e.company_id = '{id_company}'
                  )
            """
            self.logger.debug(f"get_transaction_status_by_bill_id slq: {sql}")
            conn = Tortoise.get_connection("market")
            deal_info = await conn.execute_query_dict(sql)
            self.logger.debug(f"get_transaction_status_by_bill_id result: {deal_info}")
            if not deal_info:
                self.logger.info(f"get_transaction_status_by_bill_id: transaction not found")
                return {
                    "name": "deal_by_bill",
                    "params": {
                        "phone": phone,
                        "bill_id": bill_id
                    },
                    "report": {
                        "deal_info": {},
                        "deal_detail": []
                    }
                }

            deal_info = deal_info[0]
            cashier_blockchain = deal_info.get('cashier_blockchain')

            sql = f"""
                select
                    case
                        when dd.blockchain = '{cashier_blockchain}'  then '-' else '+' 
                    end operation,
                    case
                        when (dd.phone = '{phone}' or dd.blockchain = '{cashier_blockchain}') then dd.phone else 'secured' 
                    end phone,
                    dd.name token_name,
                    dd.token_uuid::text,
                    dd.amount
                from (
                        select p.phone, p.blockchain , t."name", t.uuid token_uuid, dt.amount
                        from public.marketcore_deal d
                            join public.marketcore_deal_part dp on dp.deal_id = d.id
                            join marketcore_profile p on p.blockchain = dp.participant 
                            left join public.marketcore_deal_token dt on dt.deal_part_id = dp.id 
                            left join public.marketcore_token t on t.id = dt.token_id
                        where d.deal_client_id = '{bill_id}'
                ) as dd
            """
            self.logger.debug(f"get_transaction_status_by_bill_id slq: {sql}")
            conn = Tortoise.get_connection("market")
            deal_detail = await conn.execute_query_dict(sql)
            self.logger.debug(f"get_transaction_status_by_bill_id result: {deal_detail}")

            report = {
                "name": "deal_by_bill",
                "params": {
                    "phone": phone,
                    "bill_id": bill_id
                },
                "report": {
                    "deal_info": deal_info,
                    "deal_detail": deal_detail
                }
            }

            return report
        except Exception as e:
            self.logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
            return None

    async def company_report_by_phone(self, id_company, phone, from_date_str=None, to_date_str=None):
        try:
            phone = str(phone).replace('+', '')
            from_date_filter = f""" and h."date" >= TO_TIMESTAMP('{from_date_str}', 'YYYY-MM-DD HH24:MI:ss') """ \
                if from_date_str else ""
            to_date_filter = f""" and h."date" <= TO_TIMESTAMP('{to_date_str}' , 'YYYY-MM-DD HH24:MI:ss')""" \
                if to_date_str else ""
            sql = f"""
                select
                    to_char(h."date",'YYYY-MM-DD HH24:MI:SS') operation_date,  
                    p.phone "user",
                    p1.phone "your_user", 
                    coalesce (e.internal_name, p1.username) your_user_name,
                    h.amount operation_amount,
                    case 
                        when h."type" = 'CREDIT' then '-' else '+'
                    end operation,
                    case 
                        when t.blockchain_provider = c.blockchain_owner_id then h.balance else 0 
                    end balance,
                    t."name" token_name,
                    t.uuid::text token_uuid,
                    d.deal_type,
                    d.deal_status,
                    d.error_message,
                    d.deal_client_id,
                    d."comment" 
                from public.marketcore_transfer_history h
                    left join public.marketcore_employee e on e.profile_blockchain = h.recipient 
                    left join public.marketcore_company c on c.id = e.company_id 
                    join public.marketcore_profile p on p.blockchain = h.profile_blockchain 
                    join public.marketcore_profile p1 on p1.blockchain = h.recipient 
                    join public.marketcore_token t on t.id = h.token_id 
                    join public.marketcore_deal d on h.source_id = d.id 
                where
                    p.phone = '{phone}'
                    and e.company_id = '{id_company}'
                    {from_date_filter}
                    {to_date_filter}
                order by d.create_ts desc
            """
            self.logger.debug(f"company_report_by_phone slq: {sql}")
            conn = Tortoise.get_connection("market")
            report = await conn.execute_query_dict(sql)
            self.logger.debug(f"company_report_by_phone result: {report}")
            if not report:
                self.logger.error(f"company_report_by_phone: no data")
                return {
                    "name": "company_report_by_phone",
                    "params": {
                        "phone": phone,
                        "from_date": from_date_str,
                        "to_date": to_date_str
                    },
                    "report": []
                }

            report = {
                "name": "company_report_by_phone",
                "params": {
                    "phone": phone,
                    "from_date": from_date_str,
                    "to_date": to_date_str
                },
                "report": report
            }
            return report
        except Exception as e:
            self.logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
            return None


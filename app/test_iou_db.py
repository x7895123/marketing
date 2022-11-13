import asyncio
from pprint import pprint
from tortoise import Tortoise


async def run():
    config = {
        'connections': {
            # Dict format for connection
            'marketing': {
                'engine': 'tortoise.backends.asyncpg',
                'credentials': {
                    'host': '192.168.90.221',
                    'port': '6000',
                    'user': 'arena',
                    'password': 'arenajkfmg7pdo5',
                    'database': 'iou',
                }
            },
            'market': {
                'engine': 'tortoise.backends.asyncpg',
                'credentials': {
                    'host': '192.168.90.85',
                    'port': '5432',
                    'user': 'postgres',
                    'password': 'QWERTY654321',
                    'database': 'market',
                },
            },
        },
        'apps': {}
    }
    await Tortoise.init(config=config)


async def get_access_token(username):
    conn = Tortoise.get_connection("market")
    sql = f"""
                select token_value
                from public.sys_access_token t
--                where t.user_login = '{username}' and current_timestamp < expiry
                where t.user_login = '01kz' and current_timestamp < expiry
                order by create_ts desc
                limit 1
    """
    print(sql)
    if result := await conn.execute_query_dict(sql):
        print(f"get_access_token result: {result}")
        token = result[0].get('token_value')
        print(f"get_access_token: {token}")
        if token:
            return token
        else:
            return ""
    else:
        return ""


async def get_deferred_task(id_company, phone):
    conn = Tortoise.get_connection("marketing")
    sql = f"""
            select
                id,
                id_company, 
                phone,  
                task ->> 'msg' msg,	
                replace(replace(task ->> 'ids1', '[', '{{'), ']', '}}')::int[] ids1,
                replace(replace(task ->> 'amounts1', '[', '{{'), ']', '}}')::int[] amounts1
            from public.marketing_deferred_task
            where phone = '{phone}' and id_company = '{id_company}' and sent_date is null
    """
    print(f"marketing get_deferred_task sql: {sql}")
    result = await conn.execute_query_dict(sql)
    print(result)


async def main():
    await run()
    id_company = '8647480b-2fae-f467-3991-b0ffb2923258'
    phone = '+77015552258'
    await get_deferred_task(id_company, phone)
    # print(f" access_token: {await get_access_token('01kz')}")


if __name__ == '__main__':
    results = asyncio.run(main())

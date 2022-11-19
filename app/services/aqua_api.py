import asyncio
import httpx

from app.shared.settings import aqua_api_host
from sanic.log import logger


def prepare_sql(sql):
    sql = sql.replace("\n", " ")
    sql = ' '.join(sql.split())
    return sql


async def json_request(url, payload: dict):
    try:
        headers = {
            'Authorization': f'Basic ZHVkZTpIb2xkIE15IEJlZXI=',
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, json=payload, timeout=10)

        logger.info(f'json_request: {response.text}')
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        logger.error(f"json_request: {e}")
        return {}


async def select_request(sql):
    url = f"http://{aqua_api_host}/dql"
    payload = {"sql": prepare_sql(sql)}
    return await json_request(url, payload)


async def dml_request(sql):
    url = f"http://{aqua_api_host}/dml"
    payload = {"sql": prepare_sql(sql)}
    return await json_request(url, payload)


async def get_qr(data):
    try:
        url = "http://{}/qr".format(aqua_api_host)
        payload = {"data": data, "from_color": "#000956", "to_color": "#503056"}
        # print(payload)

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json=payload, timeout=10)

        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        logger.error(f"json_request: {e}")
        return None


if __name__ == '__main__':
    # print(select_request("select id, name from ud_user_roles where bot = 'DELIVERY_FOODBOT' and id < 5"))
    # asyncio.run(dml_request("update ud_cashback set token_id = null where id = 16906"))
    print(asyncio.run(dml_request("select payment from ud_cashback where id = 16906")))





import httpx
import json
from sanic.log import logger


async def get_auth_token(dostyq_marketing_authorization):
    try:
        headers = {'Authorization': dostyq_marketing_authorization}
        url = 'https://marketing.dostyq.app/login'
        async with httpx.AsyncClient() as client:
            response = await client.request("POST", url, headers=headers, timeout=15)
        if response.status_code == 200:
            logger.debug(f"get_auth_token: {response.content}")
            return response.text
        else:
            logger.error(f"get_auth_token {response.status_code} {response.content}")
            return ""
    except Exception as e:
        logger.error(f"get_auth_token: {e}")
    return ""

send_gift_results = {
    0: "Gift sent successfully",
    1: "Gift already sent",
    -1: "Send Gift error",
}


async def send_gift(dostyq_marketing_authorization, gift: dict):
    try:
        auth_token = await get_auth_token(dostyq_marketing_authorization)
        if auth_token:
            url = "https://marketing.dostyq.app/send_gift"

            headers = {
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, headers=headers, json=gift, timeout=10)

            if response.status_code == 200:
                logger.info(f'send_gift: {response.text}')
                return 0
            elif 'already exists' in response.text:
                logger.info(f'send_gift: {response.text}')
                return 1
            else:
                logger.error(f'send_gift {response.text} {response.status_code}')
            return -1
    except Exception as e:
        logger.error(f"send_gift: {e}")
        return -1


if __name__ == '__main__':
    pass

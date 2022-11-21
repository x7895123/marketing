import inspect
import rapidjson
import tortoise.timezone
from sanic.log import logger
from app.rabbit.rabbit import Rabbit
from app.services import dostyq_marketing
from app.models import bills


async def send_gift(message, publisher: Rabbit):
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

    try:
        logger.debug(f"Send Gift Received {message.body}")
        bill_dict = rapidjson.loads(message.body)
        gift_id = bill_dict.get('gift_id')
        gift = await bills.MarketingGift.get(id=gift_id)
        bill_id = gift.bill_id
        logger.info(f"bill_id: {bill_id}")
        bill = await bills.MarketingBill.get(id=bill_id)

        company = bill.company
        cashdesk = bill.cashdesk
        assignment = gift.assignment
        screen_msg = gift.screen_msg
        phone = bill.phone
        deal = gift.deal

        gift_dict = {
            "phone": phone,
            "bill_id": f"{company}-{assignment}-{gift_id}",
            "delay": 0,
            **deal
        }

        if await dostyq_marketing.send_gift(gift_dict, company) >= 0:
            await bills.MarketingGift.filter(id=gift_id).update(
                sent_ts=tortoise.timezone.now()
            )
            if screen_msg:
                screen_msg_queue_name = f"{company}_{cashdesk}_show_bonus"
                body = rapidjson.dumps({"comment": gift.screen_msg})
                await publisher.publish(
                    body=body,
                    queue_name=screen_msg_queue_name
                )

        else:
            await publisher.ttl_publish(
                body=message.body,
                queue_name='send_gift',
                minutes=10
            )

        await message.ack()
    except Exception as e:
        logger.error(f'{inspect.stack()[0][1]} {inspect.stack()[0][3]}: {e}')
        await publisher.ttl_publish(
            body=message.body,
            queue_name='send_gift',
            minutes=10
        )

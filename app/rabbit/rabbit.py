import json
import time
from typing import Optional, Any, Coroutine

import aio_pika
import inflect
import rapidjson
from aio_pika import ExchangeType, Message, IncomingMessage
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from sanic.log import logger

from app.shared.settings import get


def parse_delay(days=0, hours=0, minutes=0, seconds=0):
    return int(abs(days)) * 60000 * 60 * 24 + \
           int(abs(hours)) * 60000 * 60 + \
           int(abs(minutes)) * 60000 + \
           int(abs(seconds)) * 1000


def delay2name(delay):
    p = inflect.engine()
    hours = delay // (60000 * 60)
    if hours > 0:
        # print(f"{p.number_to_words(hours)}_hours")
        return f"{p.number_to_words(hours)}_hours"
    else:
        minutes = delay // 60000
        # print(f"{p.number_to_words(minutes)}_min")
        return f"{p.number_to_words(minutes)}_min"


class Rabbit:

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None

    async def connect(self):
        attempts = 0
        while True:
            attempts += 1
            try:
                return await aio_pika.connect_robust(host=self.host,
                                                     login=self.user,
                                                     password=self.password,
                                                     port=self.port)
            except Exception as why:
                print(why)
                time.sleep(min(attempts * 2, 30))
            except KeyboardInterrupt:
                break

    async def get(self, queue_name) -> Coroutine[Any, Any, AbstractIncomingMessage | None] | bool:
        try:
            await self.check_connection()
            channel = await self.connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)
            message = await queue.get()
            async with message.process():
                return rapidjson.loads(message.body)

        except Exception as e:
            logger.error(f'publish get: {e}')
            await self.connection.close()
            return False

    async def check_connection(self):
        if not self.connection:
            logger.info(f'connection not defined')
            self.connection = await self.connect()
        if self.connection.is_closed:
            logger.info(f'is closed: {self.connection.is_closed}')
            self.connection = await self.connect()

    async def ttl_publish(self, body, queue_name, hours=0, minutes=0):
        try:
            await self.check_connection()

            channel = await self.connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)
            if hours + minutes == 0:
                await channel.default_exchange.publish(Message(body.encode('utf-8')), routing_key=queue_name)
            else:
                await queue.bind('amq.direct', queue_name)
                delay_channel = await self.connection.channel()
                delay = 60000 * (hours * 60 if hours > 0 else minutes)
                delayed_queue_name = f'{queue_name}_{delay2name(delay)}'
                await delay_channel.declare_queue(delayed_queue_name, durable=True, arguments={
                        'x-message-ttl': delay,  # Delay until the message is transferred in milliseconds.
                        'x-dead-letter-exchange': 'amq.direct',  # Exchange used to transfer the message from A to B.
                        'x-dead-letter-routing-key': queue_name  # Name of the queue we want the message transferred to.
                    })
                await delay_channel.default_exchange.publish(Message(body.encode('utf-8')),
                                                             routing_key=delayed_queue_name)
                return True
        except Exception as e:
            logger.error(f'simple_publish: {e}')
            await self.connection.close()
            return False

    async def publish(self, body, queue_name, delay=0):

        try:
            delay = int(abs(delay))
            logger.debug(f'publish {body}')
            await self.check_connection()

            channel = await self.connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)
            if delay == 0:
                await channel.default_exchange.publish(Message(body.encode('utf-8')), routing_key=queue_name)
            else:
                exchange = await channel.declare_exchange("xdelayed",
                                                          durable=True,
                                                          type=ExchangeType.X_DELAYED_MESSAGE,
                                                          arguments={'x-delayed-type': 'direct'})

                await queue.bind(exchange, queue_name)

                await exchange.publish(
                    Message(
                        bytes(json.dumps(body), "utf-8"),
                        content_type="text/plain",
                        headers={"x-delay": delay},
                    ),
                    queue_name,
                )
            return True
        except Exception as e:
            logger.error(f'simple_publish: {e}')
            await self.connection.close()
            return False


# async def test():
#     logger = app.shared.log.set_logger('test')
#     try:
#         credentials = {
#             'host': "192.168.90.78",
#             'port': 5672,
#             'user': "test",
#             'password': "test"
#         }
#         publisher = Publisher(logger=logger, **credentials)
#         print('simple_publish')
#         async for i in trange(50):
#             # if not await publisher.simple_publish(f'HiNew{i}', 'test_queue2', 15000):
#             #     logger.error(f'test error {i}')
#             result = False
#             while not result:
#                 result = await publisher.publish(f'ddd{i}', 'test_queue4', 5000)
#                 if not result:
#                     time.sleep(5)
#
#         # print('\npublish')
#         # async for i in trange(20):
#         #     await publisher.publish(f'HiNew{i}', 'test_queue2', *d)
#     except Exception as e:
#         logger.error(f'error {e}')
if __name__ == '__main__':
    pass

import json
import time

import aio_pika
from aio_pika import ExchangeType, Message


def parse_delay(days=0, hours=0, minutes=0, seconds=0):
    return int(abs(days)) * 60000 * 60 * 24 + \
           int(abs(hours)) * 60000 * 60 + \
           int(abs(minutes)) * 60000 + \
           int(abs(seconds)) * 1000


class Publisher:

    def __init__(self, logger, host, port, user, password):
        self.logger = logger
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

    async def ttl_publish(self, body, queue_name, delay=0):
        try:
            delay = int(abs(delay))
            if not self.connection:
                self.logger.info(f'connection not defined')
                self.connection = await self.connect()

            if self.connection.is_closed:
                self.logger.info(f'is closed: {self.connection.is_closed}')
                self.connection = await self.connect()

            channel = await self.connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)
            if delay == 0:
                await channel.default_exchange.publish(Message(f'Zero{body}'.encode('utf-8')), routing_key=queue_name)
            else:
                await queue.bind('amq.direct', queue_name)
                delay_channel = await self.connection.channel()
                delayed_queue_name = f'delayed_{delay}'
                await delay_channel.declare_queue(delayed_queue_name, durable=True, arguments={
                        'x-message-ttl': delay,  # Delay until the message is transferred in milliseconds.
                        'x-dead-letter-exchange': 'amq.direct',  # Exchange used to transfer the message from A to B.
                        'x-dead-letter-routing-key': queue_name  # Name of the queue we want the message transferred to.
                    })
                await delay_channel.default_exchange.publish(Message(body.encode('utf-8')),
                                                             routing_key=delayed_queue_name)
                return True
        except Exception as e:
            self.logger.error(f'simple_publish: {e}')
            await self.connection.close()
            return False

    async def publish(self, body, queue_name, delay=0):

        try:
            delay = int(abs(delay))
            self.logger.debug(f'publish {body}')
            if not self.connection:
                self.logger.info(f'connection not defined')
                self.connection = await self.connect()

            if self.connection.is_closed:
                self.logger.info(f'is closed: {self.connection.is_closed}')
                self.connection = await self.connect()

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
            self.logger.error(f'simple_publish: {e}')
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
    # asyncio.run(test())

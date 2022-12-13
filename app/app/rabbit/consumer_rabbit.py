import asyncio
import time
import aio_pika
from sanic.log import logger


async def process_message(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    async with message.process():
        print(message.body)
        # await asyncio.sleep(1)


def consume(app, callbacks, max_retries, host, port, user, password):

    async def connect():
        attempts = 0
        while True:
            attempts += 1
            try:
                return await aio_pika.connect_robust(host=host,
                                                     login=user,
                                                     password=password,
                                                     port=port)
            except aio_pika.AMQPException as why:
                print(why)
                if max_retries and attempts > max_retries:
                    return None
                time.sleep(min(attempts * 2, 30))
            except KeyboardInterrupt:
                break

    @app.listener("after_server_start")
    async def go(_app) -> None:
        connection = await connect()

        while True:
            try:
                channel = await connection.channel()
                # Maximum message count which will be processing at the same time.
                await channel.set_qos(prefetch_count=100)
                # Declaring queue
                for queue_name, callback in callbacks.items():
                    queue = await channel.declare_queue(queue_name, durable=True)
                    await queue.consume(callback)
                    logger.info(f"start consume {queue_name} ...")
                await asyncio.Future()
            except aio_pika.AMQPException as why:
                logger.error(why)
                # print(why)
                connection = await connect()
            except KeyboardInterrupt:
                await connection.close()
                break


def consume_v2(app, callbacks, max_retries):

    async def connect(host, user, password, port):
        attempts = 0
        while True:
            attempts += 1
            try:
                return await aio_pika.connect_robust(host=host,
                                                     login=user,
                                                     password=password,
                                                     port=port)
            except aio_pika.AMQPException as why:
                print(why)
                if max_retries and attempts > max_retries:
                    return None
                time.sleep(min(attempts * 2, 30))
            except KeyboardInterrupt:
                break

    @app.listener("after_server_start")
    async def go(_app) -> None:
        while True:
            try:
                for key, value in callbacks.items():
                    queue_name = value["queuename"]
                    callback = value["callback"]
                    rabbit_params = value["rabbit_params"]

                    connection = await connect(**rabbit_params)
                    channel = await connection.channel()
                    # Maximum message count which will be processing at the same time.
                    await channel.set_qos(prefetch_count=1)
                    # Declaring queue
                    queue = await channel.declare_queue(queue_name, durable=True)
                    await queue.consume(callback)
                    logger.info(f"start consume {key}-{queue_name} ...")
                await asyncio.Future()
            except aio_pika.AMQPException as why:
                logger.error(why)


if __name__ == "__main__":
    pass
    # consumer = Consumer(process_message, 'test_queue2')
    # consumer.start()
    # print('d')

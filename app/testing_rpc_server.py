import asyncio
import json
import logging

import rapidjson
from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage

from app.app.shared import settings


def fib(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


async def on_response(message: AbstractIncomingMessage):
    print(message.body)
    # n = int(message.body.decode())
    # response = str(fib(n)).encode()

    result = {"status": 1, "message": "phone_is _empty"}
    response = rapidjson.dumps(result).encode()

    dostyq_rabbit = settings.get("dostyq_rabbit")
    connection = await connect(
        host=dostyq_rabbit.get('host'),
        port=dostyq_rabbit.get('port'),
        login=dostyq_rabbit.get('user'),
        password=dostyq_rabbit.get('password')
    )

    # Creating a channel
    channel = await connection.channel()
    exchange = channel.default_exchange
    await exchange.publish(
        Message(
            body=response,
            correlation_id=message.correlation_id,
        ),
        routing_key=message.reply_to,
    )
    print("Request complete")
    await message.ack()


async def main() -> None:
    # Perform connection
    dostyq_rabbit = settings.get("dostyq_rabbit")
    connection = await connect(
        host=dostyq_rabbit.get('host'),
        port=dostyq_rabbit.get('port'),
        login=dostyq_rabbit.get('user'),
        password=dostyq_rabbit.get('password')
    )

    # Creating a channel
    channel = await connection.channel()
    exchange = channel.default_exchange

    # Declaring queue
    queue = await channel.declare_queue("aqua", durable=True)
    await queue.consume(on_response)
    await asyncio.Future()

    print(" [x] Awaiting RPC requests")


if __name__ == "__main__":
    asyncio.run(main())
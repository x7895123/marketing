import asyncio
import uuid
from typing import MutableMapping

import rapidjson
from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,
)

from app.app.shared import settings


class FibonacciRpcClient:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue
    loop: asyncio.AbstractEventLoop

    def __init__(self) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.loop = asyncio.get_running_loop()

    async def connect(self) -> "FibonacciRpcClient":
        dostyq_rabbit = settings.get("dostyq_rabbit")
        self.connection = await connect(
            host=dostyq_rabbit.get('host'),
            port=dostyq_rabbit.get('port'),
            login=dostyq_rabbit.get('user'),
            password=dostyq_rabbit.get('password'),
            loop=self.loop
        )

        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response)

        return self

    def on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return

        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, n: int) -> int:
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        body = {"uuid": "d4de1659-2adc-4add-9a42-40f508ba9c81", "phone": "77766656544"}

        body = rapidjson.dumps(body).encode()

        await self.channel.default_exchange.publish(
            Message(
                body,
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key="aqua",
        )

        return await future


async def main() -> None:
    fibonacci_rpc = await FibonacciRpcClient().connect()
    print(" [x] Requesting fib(30)")
    response = await fibonacci_rpc.call(30)
    print(f" [.] Got {response}")


if __name__ == "__main__":
    asyncio.run(main())
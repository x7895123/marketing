import asyncio
import json
import uuid
from typing import MutableMapping
from app.app.shared import settings

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,
)


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
            loop=self.loop,
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

    async def call(self):
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future
        qr_data = {
            "uuid": "643f7330-280f-40bf-b7f1-3a386944d122",
            "action": "aquaV1",
            "queueName": "aqua",
            "phone": "7010000013"
        }
        body = json.dumps(qr_data).encode()

        await self.channel.default_exchange.publish(
            Message(
                body=body,
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key="aqua",
        )

        return await future


async def main() -> None:
    fibonacci_rpc = await FibonacciRpcClient().connect()
    print(" [x] Requesting fib(30)")
    response = await fibonacci_rpc.call()
    print(f" [.] Got {response!r}")


if __name__ == "__main__":
    asyncio.run(main())


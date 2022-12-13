import asyncio
import logging

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
    queue = await channel.declare_queue("")

    print(" [x] Awaiting RPC requests")

    # Start listening the queue with name 'hello'
    async with queue.iterator() as qiterator:
        message: AbstractIncomingMessage
        async for message in qiterator:
            try:
                async with message.process(requeue=False):
                    assert message.reply_to is not None

                    n = int(message.body.decode())

                    print(f" [.] fib({n})")
                    response = str(fib(n)).encode()

                    await exchange.publish(
                        Message(
                            body=response,
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                    )
                    print("Request complete")
            except Exception:
                logging.exception("Processing error for message %r", message)

if __name__ == "__main__":
    asyncio.run(main())
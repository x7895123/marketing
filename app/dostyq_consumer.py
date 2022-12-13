import functools

from tortoise import Tortoise

from app.callbacks.auth_by_qr import process_qr_auth
from app.rabbit.consumer_rabbit import consume, consume_v2, consume_v3
from app.rabbit.rabbit import Rabbit
from app.shared import settings
from app.shared.tools import *

logger.setLevel('DEBUG')
settings.config_name = 'prod'
Tortoise.init(config=settings.get('api'))
Tortoise.generate_schemas()
rabbit_params = settings.get('arena_rabbit')
logger.info(f"rabbit_params: {rabbit_params}")
publisher = Rabbit(**rabbit_params)

# qr_auth
process_qr_auth_callback = functools.partial(
    process_qr_auth, publisher=publisher
)
process_qr_auth_queue_name = f'aqua'

arena_rabbit = settings.get('arena_rabbit')
dostyq_rabbit = settings.get("dostyq_rabbit")
logger.info(f"arena_rabbit params: {arena_rabbit}")
logger.info(f"dostyq_rabbit params: {dostyq_rabbit}")

callbacks = {
    "process_qr_auth": {
        "queuename": process_qr_auth_queue_name,
        "callback": process_qr_auth_callback,
        "rabbit_params": dostyq_rabbit
    },
}

if __name__ == "__main__":
    pass
    # consume_v3(
    #     callbacks=callbacks,
    #     max_retries=None
    # )
    # app.run(port=8000, fast=True, debug=False, access_log=True)

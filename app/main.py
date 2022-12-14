import functools

from sanic import Sanic

import tortoise.contrib.sanic
from sanic_ext import Extend

from app.callbacks.city_calc_bonus import calc_city_bonus
from app.callbacks.auth_by_qr import process_qr_auth
from app.callbacks.kiiik_calc_bonus import calc_kiiik_bonus
from app.callbacks.aqua_calc_bonus import calc_aqua_bonus

from app.send_gift_callback.send_gift import send_gift
from app.rabbit.consumer_rabbit import consume, consume_v2
from app.rabbit.rabbit import Rabbit
from app.routes.login import bp as login_bp
from app.routes.game import bp as game_bp
from app.routes.bill import bp as bill_bp
from app.routes.iiko_bill import bp as iiko_bp
from app.routes.qr import bp as qr_bp
from app.routes.admin import bp as admin_bp

from app.routes.pages import routes as pages_routes
from app.middlewares.middlewares import setup_middlewares

from app.shared import settings
from app.shared.tools import *
from sanic_cors.extension import CORS

app = Sanic('Marketing')
app.config.LOGGING = True
CORS_OPTIONS = {"resources": r'/*', "origins": "*", "methods": ["GET", "POST", "HEAD", "OPTIONS"]}
Extend(app, extensions=[CORS], config={"CORS": False, "CORS_OPTIONS": CORS_OPTIONS})

logger.setLevel('DEBUG')
app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Marketing'
app.config.API_CONTACT_EMAIL = 'vladimirsv@gmail.com'
app.config.API_DESCRIPTION = 'Integration API for business'

settings.config_name = 'prod'
# rabbit_params = settings.get('arena_rabbit')
# logger.info(rabbit_params)

# injected objects
tortoise.contrib.sanic.register_tortoise(app, config=settings.get('api'), generate_schemas=True)
rabbit_params = settings.get('arena_rabbit')
logger.info(f"rabbit_params: {rabbit_params}")
publisher = Rabbit(**rabbit_params)
app.ctx.publisher = publisher
# register_dependencies(app, publisher)

# load routes
app.blueprint(login_bp)
app.blueprint(game_bp)
app.blueprint(bill_bp)
app.blueprint(iiko_bp)
app.blueprint(qr_bp)
app.blueprint(admin_bp)
pages_routes(app)
setup_middlewares(app)

app.ext.openapi.add_security_scheme(
    "basicAuth",
    "http",
    scheme="basic",
)

app.ext.openapi.add_security_scheme(
    "bearerAuth",
    "http",
    scheme="bearer",
)

# app.static('/static', './static', name='static')
# app.static('/img', './static/img', name='img')
# app.static('/css', './static/css', name='css')

# start page
app.static('/assets', './templates/start_page/assets', name='assets')
app.static('/', './templates/start_page', name='start_page')

# spin
app.static('/Build', './static/Build', name='Build')
app.static('/TemplateData', './static/TemplateData', name='TemplateData')
app.static('/StreamingAssets', './static/StreamingAssets', name='StreamingAssets')

# slot
app.static('/slot/Build', './static/slot/Build', name='slotBuild')
app.static('/slot/TemplateData', './static/slot/TemplateData', name='slotTemplateData')
app.static('/slot/StreamingAssets', './static/slot/StreamingAssets', name='slotStreamingAssets')

# spinV2
app.static('/spinV2/Build', './static/spinV2/Build', name='spinV2Build')
app.static('/spinV2/TemplateData', './static/spinV2/TemplateData', name='spinV2TemplateData')
app.static('/spinV2/StreamingAssets', './static/spinV2/StreamingAssets', name='spinV2StreamingAssets')


# app.static('/templates', './templates', name='templates')
# app.static('/build', './templates/build', name='build')
# app.static('/templatedata', './templates/templatedata', name='templatedata')


# Rabbit Consumer Thread

# # charge consumer
# send_delayed_gift = functools.partial(app.ctx.gift.send_delayed_gift, services=app.ctx)
# app.ctx.charge_bonus_queue_name = f'charge_bonus_{str(settings.environment).lower()}'
#
# # Bill consumer
# app.ctx.bill_queue_name = f'bill_{str(settings.environment).lower()}'
# app.ctx.calculated_bill_queue_name = f'calculated_bill_{str(settings.environment).lower()}'
# # logger.debug(f"calculated_bill_queue_name: {app.ctx.calculated_bill_queue_name}")
# process_calculated_bill = functools.partial(app.ctx.bill.process_calculated_bill, services=app.ctx)
# # process_calculated_bill_consumer = consume(
#
# aqua
calc_aqua_bonus_callback = functools.partial(
    calc_aqua_bonus, publisher=publisher
)
calc_aqua_bonus_queue_name = f'aqua_calc_bonus'

# city
calc_city_bonus_callback = functools.partial(
    calc_city_bonus, publisher=publisher
)
calc_city_bonus_queue_name = f'city_calc_bonus'

# kiiik
calc_kiiik_bonus_callback = functools.partial(
    calc_kiiik_bonus, publisher=publisher
)
calc_kiiik_bonus_queue_name = "kiiik_calc_bonus"

# send gift
send_gift_callback = functools.partial(
    send_gift, publisher=publisher
)
send_gift_queue_name = f'send_gift'

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
    "calc_aqua_bonus": {
        "queuename": calc_aqua_bonus_queue_name,
        "callback": calc_aqua_bonus_callback,
        "rabbit_params": arena_rabbit
    },
    "calc_city_bonus": {
        "queuename": calc_city_bonus_queue_name,
        "callback": calc_city_bonus_callback,
        "rabbit_params": arena_rabbit
    },
    "calc_kiiik_bonus": {
        "queuename": calc_kiiik_bonus_queue_name,
        "callback": calc_kiiik_bonus_callback,
        "rabbit_params": arena_rabbit
    },
    "send_gift": {
        "queuename": send_gift_queue_name,
        "callback": send_gift_callback,
        "rabbit_params": arena_rabbit
    },
}

consume_v2(
    app=app,
    callbacks=callbacks,
    max_retries=None
)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, fast=True, debug=False, access_log=True)
    # app.run(port=8000, fast=True, debug=False, access_log=True)

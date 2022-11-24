import functools

from sanic import Sanic

import tortoise.contrib.sanic

from app.calc_bonus_callbacks.kiiik_calc_bonus import calc_kiiik_bonus
from app.calc_bonus_callbacks.aqua_calc_bonus import calc_aqua_bonus

from app.send_gift_callback.send_gift import send_gift
from app.rabbit.consumer_rabbit import consume
from app.rabbit.rabbit import Rabbit
from app.routes.login import bp as login_bp
from app.routes.game import bp as game_bp
from app.routes.bill import bp as bill_bp

from app.routes.pages import routes as pages_routes
from app.middlewares.middlewares import setup_middlewares

from app.shared import settings
from app.shared.tools import *



app = Sanic('Marketing')
app.config.LOGGING = True
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

app.static('/static', './static', name='static')
app.static('/img', './static/img', name='img')
app.static('/css', './static/css', name='css')

app.static('/Build', './static/build', name='build')
app.static('/TemplateData', './static/TemplateData', name='TemplateData')


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

callbacks = {
    calc_aqua_bonus_queue_name: calc_aqua_bonus_callback,
    calc_kiiik_bonus_queue_name: calc_aqua_bonus_callback,
    send_gift_queue_name: send_gift_callback,
}

consume(
    app=app,
    callbacks=callbacks,
    max_retries=None,
    **rabbit_params
)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, fast=True, debug=False, access_log=True)
    # app.run(port=8000, fast=True, debug=False, access_log=True)

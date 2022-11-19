import functools

from sanic import Sanic

import tortoise.contrib.sanic

from dependencies.dependencies import register_dependencies
from routes.login import bp as login_bp
from routes.game import bp as game_bp
from routes.bill import bp as bill_bp

from routes.pages import routes as pages_routes
from middlewares.middlewares import setup_middlewares

from shared import settings
from shared.tools import *

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
register_dependencies(app)

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

# Rabbit Consumer Thread
# calc_aqua_bonus = functools.partial(app.ctx.gift.send_delayed_gift, services=app.ctx)
# app.ctx.charge_bonus_queue_name = f'charge_bonus_{str(settings.environment).lower()}'



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
# callbacks = {
#     app.ctx.charge_bonus_queue_name: send_delayed_gift,
#     app.ctx.calculated_bill_queue_name: process_calculated_bill
# }
#
# consume(
#     app=app,
#     callbacks=callbacks,
#     max_retries=None,
#     **rabbit_params
# )

# app.listener('before_server_start')(consumer.connect)
# app.listener('after_server_start')(charge_bonus_consumer.go)
# app.listener('after_server_start')(process_calculated_bill_consumer.go)
# app.listener('before_server_stop')(charge_bonus_consumer.close_connection)
# app.listener('before_server_stop')(process_calculated_bill_consumer.close_connection)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, fast=True, debug=False, access_log=True)

import functools

from sanic import Sanic

import tortoise.contrib.sanic

from routes.login import bp as login_bp
from routes.pages import routes as pages_routes
from middlewares.middlewares import setup_middlewares

from rabbit.consumer_rabbit import consume
from rabbit.publisher_rabbit import Publisher
from shared.settings import *
from shared.tools import *

app = Sanic('Marketing')
app.config.LOGGING = True
logger.setLevel('DEBUG')
app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Marketing'
app.config.API_CONTACT_EMAIL = 'vladimirsv@gmail.com'
app.config.API_DESCRIPTION = 'Integration API for business'

# injected objects
settings_name = 'prod'
rabbit_params = get('rabbit')
logger.info(rabbit_params)

tortoise.contrib.sanic.register_tortoise(app, config=get('api'), generate_schemas=True)
app.ctx.publisher = Publisher(**rabbit_params)

# load routes
app.blueprint(login_bp)
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

# # Rabbit Consumer Thread
#
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
    app.run(host='0.0.0.0', port=8080, fast=True, debug=False, access_log=True)

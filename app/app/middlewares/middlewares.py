import secure
from sanic.log import logger

from ..services import marketing_db

secure_headers = secure.Secure().framework


def setup_middlewares(app):
    @app.middleware('response')
    async def set_secure_headers(request, response):
        secure_headers.sanic(response)

    @app.middleware("request")
    async def save_log(request):
        logger.info(f"save log request.ip: {request.ip}")

    @app.middleware("request")
    async def extract_company(request):
        logger.info(f"extract_company request.token: {request.token}")
        try:
            if str(request.token).startswith('Basic'):
                request.ctx.company = await marketing_db.get_user_company(request.credentials.username)
                logger.info(f"extract_company : {request.ctx.company}")
        except Exception as e:
            logger.warning(f"extract_company exception: {e}")
            request.ctx.company = None




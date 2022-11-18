import secure
from sanic.log import logger

secure_headers = secure.Secure().framework


def setup_middlewares(app):
    @app.middleware('response')
    async def set_secure_headers(request, response):
        secure_headers.sanic(response)

    @app.middleware("request")
    async def save_log(request):
        print(f"save log request.ip: {request.ip}")

    @app.middleware("request")
    async def extract_company(request):
        print(f"extract_company request.token: {request.token}")
        # if token := request.token:
        try:
            request.ctx.company = request.credentials.username
            logger.info(f"extract_company : {request.ctx.company}")
        except Exception as e:
            logger.warning(f"extract_company exception: {e}")
            request.ctx.company = None




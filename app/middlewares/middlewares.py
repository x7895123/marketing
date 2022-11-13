import secure

secure_headers = secure.Secure().framework


def setup_middlewares(app):
    @app.middleware('response')
    async def set_secure_headers(request, response):
        secure_headers.sanic(response)

    @app.middleware("request")
    async def save_log(request):
        print(f"save log request.ip: {request.ip}")

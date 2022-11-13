import secure

secure_headers = secure.Secure().framework


def setup_middlewares(app):
    @app.middleware('response')
    async def set_secure_headers(request, response):
        secure_headers.sanic(response)

    @app.middleware("request")
    async def extract_company(request):
        print(f"extract_company request.token: {request.token}")
        # if token := request.token:
        request.ctx.id_company = await app.ctx.iou_db.get_id_company(request)
        print(f"extract_company id_company: {request.ctx.id_company}")

    @app.middleware("request")
    async def save_log(request):
        print(f"save log request.ip: {request.ip}")

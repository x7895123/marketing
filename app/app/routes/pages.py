from sanic.log import logger
from sanic_ext import openapi


def routes(app):

    partners = {
        "aqua": {
            "partner": "Аквапарк «Дельфин»",
            "partner_logo": "img/aqua.svg",
            "logo_width": 170
        },
        "kiiik": {
            "partner": "Kiiik",
            "partner_logo": "img/Kiiik.png",
            "logo_width": 107
        },
        "arena": {
            "partner": "Cyberclub «Arena»",
            "partner_logo": "img/arena.png",
            "logo_width": 107
        },
        "": {
            "partner": "Kiiik",
            "partner_logo": "img/Kiiik.png",
            "logo_width": 107
        },

    }

    # @app.get("/")
    # @app.ext.template("index.html")
    # async def handler(request):
    #     return {"seq": ["one", "two"]}

    @app.route("/")
    @openapi.definition(
        exclude=True
    )
    @app.ext.template("start_page/index.html")
    async def main(request):
        partner_id = request.get_args(keep_blank_values=True).get("")
        logger.info(f"partner_id: {partner_id}")
        if partner_param := partners.get(partner_id):
            return partner_param
        else:
            return partners.get("")

    @app.route("/x3")
    @openapi.definition(
        exclude=True
    )
    @app.ext.template("index.html")
    async def query_string(request):
        partner_id = request.get_args(keep_blank_values=True).get("")
        logger.info(f"partner_id: {partner_id}")
        if partner_param := partners.get(partner_id):
            return partner_param
        else:
            return partners.get("")

    @app.get("/terms")
    @openapi.definition(
        exclude=True,
    )
    @app.ext.template("terms.html")
    async def terms(request):
        return {}

    @app.get("/slot")
    @openapi.definition(
        exclude=True,
    )
    @app.ext.template("slot.html")
    async def slot(request):
        return {}

    @app.get("/spinV2")
    @openapi.definition(
        exclude=True,
    )
    @app.ext.template("spinV2.html")
    async def spinV2(request):
        return {}

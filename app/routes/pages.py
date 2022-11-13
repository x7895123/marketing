from sanic_ext import openapi
from sanic_ext.extensions.openapi import definitions

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
    @app.ext.template("index.html")
    async def query_string(request):
        partner_id = request.get_args(keep_blank_values=True).get("")
        app.ctx.logger.info(f"partner_id: {partner_id}")
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
        # """
        # openapi:
        # ---
        # operationId: terms
        # tags:
        #   - pages
        # """

        return {}

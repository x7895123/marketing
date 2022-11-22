# from app.rabbit.rabbit import Rabbit
# from app.shared.settings import get
#
#
# def register_dependencies(app, publisher: Rabbit):
#     @app.before_server_start
#     async def register(_, loop):
#         app.ext.dependency(publisher)

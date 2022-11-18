from app.rabbit.rabbit import Rabbit
from app.shared.settings import get


def register_dependencies(app):
    @app.before_server_start
    async def register(_, loop):
        rabbit_params = get('arena_rabbit')
        publisher = Rabbit(**rabbit_params)
        app.ext.dependency(publisher)

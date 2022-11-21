settings = {
    "prod": {
        "environment": "test",
        "arena_rabbit": {
            "host": "192.168.90.221",
            "port": 5672,
            "user": "admin",
            "password": "rabbitjkfmg7pdo5"
        },
        "aqua_rabbit": {
            "host": "192.168.90.221",
            "port": 5673,
            "user": "aqua",
            "password": "aquajkfmg7pdo5"
        },
        "dostyq_marketing_authorization": {
            "aqua": "Basic YXF1YWtyZzphcXVhSmtmbWc3cGRvNSE=",
        },
        "aqua_api_host": "192.168.90.221:4042",
        "api": {
            'connections': {
                # Dict format for connection
                'arena': {
                    'engine': 'tortoise.backends.asyncpg',
                    'credentials': {
                        'host': '192.168.90.221',
                        'port': '6000',
                        'user': 'arena',
                        'password': 'arenajkfmg7pdo5',
                        'database': 'arena',
                    }
                },
            },
            'apps': {
                'models': {
                    'models': ['models.bills', "aerich.models"],
                    # If no default_connection specified, defaults to 'default'
                    'default_connection': 'arena',
                }
            }
        }
    }
}


def get(_path):
    param = settings.get(config_name)
    for _ in _path.split('/'):
        param = param.get(_)
    return param


config_name = 'prod'
environment = get('environment')
rabbit_host = get('aqua_rabbit/host')
rabbit_port = get('aqua_rabbit/port')
rabbit_user = get('aqua_rabbit/user')
rabbit_password = get('aqua_rabbit/password')
aqua_api_host = get('aqua_api_host')
dostyq_marketing_authorization = get('dostyq_marketing_authorization')


if __name__ == "__main__":
    s = get('rabbit')
    print(s)

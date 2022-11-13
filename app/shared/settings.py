settings = {
    "prod": {
        "environment": "test",
        "rabbit": {
            "host": "192.168.90.221",
            "port": 5672,
            "user": "admin",
            "password": "rabbitjkfmg7pdo5"
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
                    'models': ['models.bills'],
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
rabbit_host = get('rabbit/host')
rabbit_port = get('rabbit/port')
rabbit_user = get('rabbit/user')
rabbit_password = get('rabbit/password')
aqua_api_host = get('aqua_api_host')


if __name__ == "__main__":
    s = get('rabbit')
    print(s)

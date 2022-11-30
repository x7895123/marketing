TORTOISE_ORM = {
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
                    'models': [
                        # 'app.app.models.bills',
                        'app.app.models.users',
                        "aerich.models"
                    ],
                    # If no default_connection specified, defaults to 'default'
                    'default_connection': 'arena',
                }
            }
        }
i# session
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS = {
    'host': '13.124.140.169',
    'port': 6379,
    'db': 0,
    'prefix': 'session',
    'socket_timeout': 1,
    'retry_on_timeout': False,
    'password': 'passw0rd!**'
}

# cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://:passw0rd!**@13.124.140.169:6379'
    }
}

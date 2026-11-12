from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        # common은 앱이 아니어서 캐시 무효화 시그널을 여기서 연결한다(모든 앱이 로드된 뒤).
        from common import cache_invalidation

        cache_invalidation.connect()

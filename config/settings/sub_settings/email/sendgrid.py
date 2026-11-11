from decouple import config

# https://github.com/sklarsa/django-sendgrid-v5
# pip install django-sendgrid-v5

# django-sendgrid-v5는 HTTP timeout을 넘기지 않으므로 timeout을 적용한 하위 클래스를 쓴다.
EMAIL_BACKEND = "utils.email.backends.TimeoutSendgridBackend"
SENDGRID_TIMEOUT = 10  # seconds
SENDGRID_API_KEY = config('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER = config('SENDGRID_DEFAULT_FROM_EMAIL')

SENDGRID_SANDBOX_MODE_IN_DEBUG = False

MAIL_VENDOR = 'sendgrid'

from decouple import config

# https://github.com/sklarsa/django-sendgrid-v5
# pip install django-sendgrid-v5

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = config('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = config('SENDGRID_DEFAULT_FROM_EMAIL')

SENDGRID_SANDBOX_MODE_IN_DEBUG = False

MAIL_VENDOR = 'sendgrid'

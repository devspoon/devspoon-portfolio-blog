from decouple import config

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = config('AWS_SES_REGION_NAME')

EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_ENDPOINT = config('AWS_SES_REGION_ENDPOINT')

MAIL_VENDOR = 'aws_ses'
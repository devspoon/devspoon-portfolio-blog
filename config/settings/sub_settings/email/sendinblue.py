from decouple import config

ANYMAIL = {
    "SENDINBLUE_API_KEY" : config('SENDINBLUE_EMAIL_HOST_API'),
    "SENDINBLUE_SENDER_DOMAIN" : config('SENDINBLUE_EMAIL_DOMAIN'),
    "SENDINBLUE_API_URL" : "https://api.sendinblue.com/v3/",
}
EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER = config('SENDINBLUE_EMAIL_HOST_USER')  # if you don't already have this in settings
SERVER_EMAIL = config('SENDINBLUE_EMAIL_HOST_USER') # ditto (default from-email for Django errors)
EMAIL_FROM = config('SENDINBLUE_EMAIL_HOST_USER')

MAIL_VENDOR = 'sendinblue'


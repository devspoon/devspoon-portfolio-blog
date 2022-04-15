import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from config.settings.base import BASE_DIR

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
AWS_ACCESS_KEY_ID = 'AKIAWZD4IGIAYN6J5OGO'
AWS_SECRET_ACCESS_KEY = '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'
AWS_SES_REGION_NAME = 'ap-northeast-2'

AWS_STORAGE_BUCKET_NAME = 'taling-bucket1'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400'
}
AWS_DEFAULT_ACL = 'public-read'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STATIC_URL = 'https://%s/static/' % AWS_S3_CUSTOM_DOMAIN
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# MEDIA_URL = '/media/'
# MEDIA_ROOT = 'media'
DEFAULT_FILE_STORAGE = 'table_bookings.config.MediaStorage'
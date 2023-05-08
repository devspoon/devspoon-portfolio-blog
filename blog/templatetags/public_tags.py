import logging

from django import template
from django.conf import settings

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))
register = template.Library()


@register.filter(name="filename")
def get_filename(full_file_path):
    temp = str(full_file_path)
    temp_list = temp.split("/")

    return temp_list[-1]

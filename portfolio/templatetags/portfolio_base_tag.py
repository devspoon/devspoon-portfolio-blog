import logging

from django import template
from django.conf import settings

logger = logging.getLogger(getattr(settings, "PORTFOLIO_LOGGER", "django"))
register = template.Library()


@register.filter(name="split_comma")
def split_string_using_comma(data):
    if not data:
        return data
    str_array = data.split(",")
    return str_array


@register.simple_tag
def update_variable(value):
    """Allows to update existing variable in template"""
    return value


@register.simple_tag
def get_verbose_name(object, fieldnm):
    return object._meta.get_field(fieldnm).verbose_name

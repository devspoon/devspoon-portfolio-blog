from django import template
import datetime

register = template.Library()

@register.filter(name='split_comma')
def split_string_using_comma(data):
    if not data :
        return data
    str_array = data.split(',')
    return str_array

@register.simple_tag
def update_variable(value):
    """Allows to update existing variable in template"""
    return value
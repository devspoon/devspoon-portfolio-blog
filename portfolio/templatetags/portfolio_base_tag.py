from django import template

register = template.Library()

@register.filter(name='split_comma')
def split_string_using_comma(data):
    if not data :
        return data
    str_array = data.split(',')
    return str_array
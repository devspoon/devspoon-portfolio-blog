from django import template

register = template.Library()

@register.filter(name='filename')
def get_filename(full_file_path):
    temp = str(full_file_path)
    temp_list = temp.split('/')

    return temp_list[-1]
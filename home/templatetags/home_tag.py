from django import template
from home.models.default import MainMenu, SiteInfo

register = template.Library()

@register.simple_tag
def main_menu_tag():
    menu = MainMenu.objects.all()
    return menu

@register.simple_tag
def site_info_tag():
    info = SiteInfo.objects.first()
    return info

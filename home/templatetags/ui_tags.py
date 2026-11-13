from django import template
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()

SPRITE = "vendor/bootstrap-icons-1.13.1/icons.svg"


@register.simple_tag
def icon(name, label=""):
    """Bootstrap Icons sprite reference. Decorative unless a label is given.
    The sprite only contains icons used in templates: run tools/build_icon_sprite.py after adding one."""
    if label:
        return format_html('<svg class="icon" role="img" aria-label="{}"><use href="{}#{}"></use></svg>',
                           label, static(SPRITE), name)
    return format_html('<svg class="icon" aria-hidden="true" focusable="false"><use href="{}#{}"></use></svg>',
                       static(SPRITE), name)

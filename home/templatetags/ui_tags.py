from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()

SPRITE = "vendor/bootstrap-icons-1.13.1/icons.svg"


@register.simple_tag
def analytics_enabled():
    """True only where settings turn analytics on (prod/stage), so dev and test pages send nothing to GA."""
    return getattr(settings, "ANALYTICS_ENABLED", False)


@register.simple_tag
def icon(name, label=""):
    """Bootstrap Icons sprite reference. Decorative unless a label is given.
    The sprite only contains icons used in templates: add the bootstrap-icons <symbol> to it before using a new one."""
    if label:
        return format_html('<svg class="icon" role="img" aria-label="{}"><use href="{}#{}"></use></svg>',
                           label, static(SPRITE), name)
    return format_html('<svg class="icon" aria-hidden="true" focusable="false"><use href="{}#{}"></use></svg>',
                       static(SPRITE), name)

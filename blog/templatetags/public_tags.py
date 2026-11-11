import logging
import re

import nh3
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))
register = template.Library()

# Allow-list for what the default Summernote toolbar produces.
_TAGS = nh3.ALLOWED_TAGS | {"font", "iframe"}
_ATTRIBUTES = {
    **nh3.ALLOWED_ATTRIBUTES,
    "*": {"style", "class", "align"},
    "a": {"href", "target", "title"},
    "img": {"src", "alt", "width", "height", "data-filename"},
    "iframe": {"src", "width", "height", "frameborder", "allowfullscreen"},
    "font": {"color", "face", "size"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
}
_STYLE_PROPERTIES = {
    "color", "background-color", "font-family", "font-size", "font-weight",
    "font-style", "text-align", "text-decoration", "line-height", "width",
    "height", "float", "margin", "margin-left", "margin-right", "padding",
    "border", "border-collapse", "vertical-align",
}
_IFRAME_SRC = re.compile(r"^(https?:)?//(www\.)?(youtube\.com|youtube-nocookie\.com|player\.vimeo\.com)/")


def _filter_attribute(tag, attr, value):
    if tag == "iframe" and attr == "src" and not _IFRAME_SRC.match(value):
        return None
    return value


@register.filter(name="sanitize_html")
def sanitize_html(value):
    """User-authored HTML (Summernote) -> safe HTML. Use instead of |safe."""
    if not value:
        return ""
    return mark_safe(
        nh3.clean(
            str(value),
            tags=_TAGS,
            attributes=_ATTRIBUTES,
            attribute_filter=_filter_attribute,
            filter_style_properties=_STYLE_PROPERTIES,
        )
    )


@register.filter(name="filename")
def get_filename(full_file_path):
    temp = str(full_file_path)
    temp_list = temp.split("/")

    return temp_list[-1]

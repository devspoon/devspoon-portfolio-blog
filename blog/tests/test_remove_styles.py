"""remove_styles builds the list card excerpt from summernote HTML: plain text, entities decoded."""
from django.template import Context, Template

from blog.templatetags.blog_base_tag import remove_styles


def test_tags_and_styles_are_removed_and_entities_decoded():
    value = '<p style="color: red">AI&nbsp;&amp;&nbsp;ML &lt;3</p>'
    assert remove_styles(value) == "AI & ML <3"


def test_excerpt_is_escaped_once_in_the_page():
    out = Template("{% load blog_base_tag %}{{ v|remove_styles }}").render(Context({"v": "<p>A&nbsp;&amp;&nbsp;B</p>"}))
    assert out == "A &amp; B"

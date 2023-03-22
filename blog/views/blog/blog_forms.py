import logging

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from blog.models.blog import BlogPost

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class BlogForm(forms.ModelForm):
    tag_set = forms.CharField(
        label="tags", help_text=_('Separate tags using ","'), required=False, initial=""
    )

    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["content"].required = True

        self.fields["content"].widget.attrs.update(
            {
                "placeholder": _("Enter Content"),
                "class": "form-control",
                "autofocus": True,
            }
        )

    class Meta:
        model = BlogPost
        fields = ["title", "content", "link1", "link2", "file1", "file2"]
        # fields = "__all__"
        labels = {
            "link1": "link1",
            "link2": "link2",
            "title": "title",
            "content": "content",
            "file1": "file1",
            "file2": "file2",
        }
        widgets = {"content": SummernoteWidget()}

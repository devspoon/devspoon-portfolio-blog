import logging

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from blog.models.blog import OpenSourcePost

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class OpenSourceForm(forms.ModelForm):
    tag_set = forms.CharField(
        label=_("Tags"), help_text=_('Separate tags using ","'), required=False, initial=""
    )

    def __init__(self, *args, **kwargs):
        super(OpenSourceForm, self).__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["content"].required = True
        self.fields["dev_lang"].required = True
        self.fields["repository"].required = True

        self.fields["content"].widget.attrs.update(
            {
                "placeholder": _("Enter Content"),
                "class": "form-control",
                "autofocus": True,
            }
        )

        if self.instance and self.instance.pk:
            self.fields["tag_set"].initial = ",".join(
                str(tag.tag) for tag in self.instance.tag_set.all()
            )

    class Meta:
        model = OpenSourcePost
        fields = [
            "title",
            "role",
            "dev_lang",
            "branch",
            "repository",
            "difficulty_level",
            "content",
            "link1",
            "link2",
            "file1",
            "file2",
        ]
        # fields = "__all__"
        labels = {
            "link1": _("Link 1"),
            "link2": _("Link 2"),
            "title": _("Title"),
            "role": _("Role"),
            "content": _("Content"),
            "dev_lang": _("Language"),
            "branch": _("Branch"),
            "repository": _("Repository"),
            "difficulty_level": _("Difficulty"),
            "file1": _("Attachment 1"),
            "file2": _("Attachment 2"),
        }
        widgets = {"content": SummernoteWidget()}

import logging

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from blog.models.blog import OnlineStudyPost

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class OnlineStudyForm(forms.ModelForm):
    tag_set = forms.CharField(
        label="tags", help_text=_('Separate tags using ","'), required=False, initial=""
    )

    def __init__(self, *args, **kwargs):
        super(OnlineStudyForm, self).__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["content"].required = True
        self.fields["dev_lang"].required = True

        self.fields["content"].widget.attrs.update(
            {
                "placeholder": _("Enter Content"),
                "class": "form-control",
                "autofocus": True,
            }
        )
        if self.instance and self.instance.pk:
            self.fields["tag_set"].initial = "".join(
                tag.name for tag in self.instance.tag_set.all()
            )

    class Meta:
        model = OnlineStudyPost
        fields = [
            "title",
            "dev_lang",
            "branch",
            "difficulty_level",
            "content",
            "link1",
            "link2",
            "file1",
            "file2",
        ]
        # fields = "__all__"
        labels = {
            "link1": "link1",
            "link2": "link2",
            "title": "title",
            "content": "content",
            "dev_lang": "dev_lang",
            "branch": "branch",
            "difficulty_level": "difficulty_level",
            "file1": "file1",
            "file2": "file2",
        }
        widgets = {"content": SummernoteWidget()}

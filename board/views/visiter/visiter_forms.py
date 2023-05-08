import logging

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from board.models.board import Visiter

logger = logging.getLogger(getattr(settings, "BOARD_LOGGER", "django"))


class VisiterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VisiterForm, self).__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["content"].required = True
        self.fields["title"].initial = ""

        self.fields["content"].widget.attrs.update(
            {
                "placeholder": _("Enter Content"),
                "class": "form-control",
                "autofocus": True,
            }
        )

    class Meta:
        model = Visiter
        fields = ["title", "content"]
        labels = {
            "title": "title",
            "content": "content",
        }
        widgets = {"content": SummernoteWidget()}

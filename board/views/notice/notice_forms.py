import logging

from django import forms
from django.utils.translation import gettext_lazy as _
from board.models.board import Notice
from django_summernote.widgets import SummernoteWidget

logger = logging.getLogger(__name__)


class NoticeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NoticeForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['title'].initial = ''
        self.fields['priority'].initial = 0
        self.fields['sorting_sequence'].initial = 0

        self.fields['content'].widget.attrs.update({
            'placeholder': _('Enter Content'),
            'class': 'form-control',
            'autofocus': True,
        })

    class Meta:
        model = Notice
        fields = ["title", "content","priority","sorting_sequence"]
        labels = {
            "title": "title",
            "content": "content",
            "priority": "priority",
            "sorting_sequence": "sorting sequence",
        }
        widgets = {
            'content': SummernoteWidget()
        }
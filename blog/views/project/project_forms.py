import logging

from django import forms
from django.utils.translation import gettext_lazy as _
from blog.models.blog import ProjectPost
from django_summernote.widgets import SummernoteWidget

logger = logging.getLogger(__name__)


class ProjectForm(forms.ModelForm):

    tag_set = forms.CharField(label='tags', help_text=_('Separate tags using ","'), required=False, initial="")

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['dev_lang'].required = True
        self.fields['repository'].required = True

        self.fields['content'].widget.attrs.update({
            'placeholder': _('Enter Content'),
            'class': 'form-control',
            'autofocus': True,
        })

    class Meta:
        model = ProjectPost
        fields = ["title", "role", "dev_lang", "branch","repository", "version", "content", "link1", "link2", "file1", "file2"]
        # fields = "__all__"
        labels = {
            "link1": "link1",
            "link2": "link2",
            "title": "title",
            "role": "role",
            "version": "version",
            "content": "content",
            "dev_lang": "dev_lang",
            "branch": "branch",
            "repository": "repository",
            "file1": "file1",
            "file2": "file2"
        }
        widgets = {
            'content': SummernoteWidget()
        }
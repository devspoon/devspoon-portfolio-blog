from django import forms
from django.utils.translation import gettext_lazy as _
from blog.models.boards import OpenSourcePost
from django_summernote.widgets import SummernoteWidget
from bs4 import BeautifulSoup as Bs

class OpenSourceForm(forms.ModelForm):
    
    tags = forms.CharField(label='tags',help_text=_('Separate tags using ","'),required=False)

    def __init__(self, *args, **kwargs):
        super(OpenSourceForm, self).__init__(*args, **kwargs)
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
        model = OpenSourcePost
        fields = ["title", "role", "dev_lang", "branch","repository", "difficulty_level", "content", "link1", "link2", "file1", "file2"]
        # fields = "__all__"
        labels = {
            "link1": "link1",
            "link2": "link2",
            "title": "title",
            "role": "role",
            "content": "content",
            "dev_lang": "dev_lang",
            "branch": "branch",
            "repository": "repository",
            "difficulty_level": "difficulty_level",
            "file1": "file1",
            "file2": "file2"
        }
        widgets = {
            'content': SummernoteWidget()
        }
from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404

from blog.models.reply import OpenSourcePostReply
from django.utils.translation import gettext_lazy as _


class ReplyCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReplyCreateForm, self).__init__(*args, **kwargs)
        self.fields['comment'].required = True

    def clean(self):
        cleaned_data = super(ReplyCreateForm, self).clean()
        comment = cleaned_data.get('comment')

        if not comment:
            raise forms.ValidationError({
                'comment': [_("Comments can't be blank")]
            })

        return cleaned_data

    class Meta:
        model = OpenSourcePostReply
        fields = ('comment',)
        labels = {
            'comment': _('comment')
        }


class ReplyUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReplyCreateForm, self).__init__(*args, **kwargs)
        self.fields['comment'].required = True

    def clean(self):
        cleaned_data = super(ReplyUpdateForm, self).clean()
        comment = cleaned_data.get('comment')

        if not comment:
            raise forms.ValidationError({
                'comment': [_("Comments can't be blank")]
            })

        return cleaned_data

    class Meta:
        model = OpenSourcePostReply
        fields = ('comment',)
        labels = {
            'comment': _('comment')
        }
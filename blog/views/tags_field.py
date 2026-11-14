from django import forms
from django.core.validators import MaxLengthValidator

from blog.models.blog import TAG_MAX_LENGTH, split_tags


class TagsField(forms.CharField):
    """쉼표로 구분한 태그. 태그 하나가 DB 상한(140자)을 넘으면 폼 오류(phase6 ADR-001, D2-A)."""

    def validate(self, value):
        super().validate(value)
        for tag in split_tags(value):
            MaxLengthValidator(TAG_MAX_LENGTH)(tag)

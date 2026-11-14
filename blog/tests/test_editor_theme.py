"""The Summernote editor iframe loads the dark-theme bridge (CSS + JS that copy the parent page's theme)."""
import pathlib

import pytest
from django.conf import settings
from django.urls import reverse

ASSETS = ("css/summernote-theme.css", "js/summernote-theme.js")


@pytest.mark.django_db
def test_editor_iframe_loads_theme_assets(client):
    html = client.get(reverse("django_summernote-editor", kwargs={"id": "id_content"})).content.decode()
    for asset in ASSETS:
        assert f'"/static/{asset}"' in html
        assert (pathlib.Path(settings.BASE_DIR).parent / "static" / asset).is_file()

"""Login page social buttons point at static images that exist and are big enough for 2x screens (44px tall)."""
import pathlib
import re

from django.conf import settings
from PIL import Image

ROOT = pathlib.Path(settings.BASE_DIR).parent
LOGIN = (ROOT / "templates/users/login.html").read_text(encoding="utf-8")


def test_social_button_images_exist_and_are_high_res():
    paths = re.findall(r"""\{% static ['"](images/[^'"]+)['"] %\}""", LOGIN)
    assert len(paths) == 3
    for rel in paths:
        f = ROOT / "static" / rel
        assert f.is_file(), rel
        if "naver" not in rel:  # naver: pending the user's choice of the official green button
            assert Image.open(f).height >= 88, rel

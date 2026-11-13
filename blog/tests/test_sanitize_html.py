import pytest

from blog.templatetags.public_tags import sanitize_html


@pytest.mark.parametrize(
    "html,expected",
    [
        # nh3 normalizes style declarations ("text-align: center;" -> "text-align:center")
        ('<p style="text-align: center;"><b>bold</b> <u>u</u> <i>i</i></p>',
         '<p style="text-align:center"><b>bold</b> <u>u</u> <i>i</i></p>'),
        ("<h2>title</h2><blockquote>q</blockquote><pre>code</pre>",) * 2,
        ("<ul><li>a</li></ul><ol><li>b</li></ol>",) * 2,
        ("<table><tbody><tr><td>cell</td></tr></tbody></table>",) * 2,
        ('<span style="color: rgb(255, 0, 0);">red</span>', '<span style="color:rgb(255, 0, 0)">red</span>'),
        # images without alt get alt="" (decorative by default); an author's alt is kept
        ('<img src="/media/a.png" style="width: 50%;">', '<img alt="" src="/media/a.png" style="width:50%">'),
        ('<img src="/media/a.png" alt="chart">', '<img src="/media/a.png" alt="chart">'),
    ],
)
def test_keeps_summernote_formatting(html, expected):
    assert sanitize_html(html) == expected


def test_keeps_safe_link():
    out = sanitize_html('<a href="https://example.com" target="_blank">x</a>')
    assert 'href="https://example.com"' in out
    assert 'target="_blank"' in out


@pytest.mark.parametrize(
    "html,bad",
    [
        ("<script>alert(1)</script>ok", "<script"),
        ('<img src="x" onerror="alert(1)">', "onerror"),
        ('<p onclick="alert(1)">x</p>', "onclick"),
        ('<a href="javascript:alert(1)">x</a>', "javascript:"),
        ('<iframe src="https://evil.example/x"></iframe>', "evil.example"),
        ('<p style="background: url(javascript:alert(1))">x</p>', "javascript:"),
    ],
)
def test_strips_dangerous(html, bad):
    assert bad not in sanitize_html(html)


def test_keeps_youtube_iframe():
    html = '<iframe src="//www.youtube.com/embed/abc" width="640" height="360" frameborder="0"></iframe>'
    assert "www.youtube.com/embed/abc" in sanitize_html(html)


def test_none_is_empty():
    assert sanitize_html(None) == ""

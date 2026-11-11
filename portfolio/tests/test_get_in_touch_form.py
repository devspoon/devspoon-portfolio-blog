import pytest
from django.test import override_settings

from portfolio.forms import MESSAGE_MAX_LENGTH, GetInTouchForm

pytestmark = pytest.mark.portfolio

# Sentry DataError 이벤트에 기록된 것과 같은 형태의 16자 초과 무작위 입력
TOO_LONG_NUMBER = "8Kd93jfLq02mVzXcPq41"


def payload(**overrides):
    data = {
        "name": "hong gildong",
        "emailfrom": "hong@example.com",
        "number": "010-1234-5678",
        "subject": "project inquiry",
        "message": "hello, I would like to talk about a project.",
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize(
    "number", ["010-1234-5678", "01012345678", "011-234-5678", ""]
)
def test_valid_numbers_are_accepted(number):
    form = GetInTouchForm(payload(number=number))

    assert form.is_valid(), form.errors


def test_number_longer_than_column_is_rejected():
    """DataError: value too long for type character varying(16) 재발 방지."""
    form = GetInTouchForm(payload(number=TOO_LONG_NUMBER))

    assert not form.is_valid()
    assert "number" in form.errors


@pytest.mark.parametrize(
    "number", ["hello-world", "12345", "010-12-34", "+82-10-1234-5678"]
)
def test_malformed_numbers_are_rejected(number):
    form = GetInTouchForm(payload(number=number))

    assert not form.is_valid()
    assert "number" in form.errors


@pytest.mark.parametrize("field", ["name", "emailfrom", "subject", "message"])
def test_required_fields(field):
    form = GetInTouchForm(payload(**{field: ""}))

    assert not form.is_valid()
    assert field in form.errors


@pytest.mark.parametrize("field", ["name", "subject"])
def test_length_limited_fields(field):
    form = GetInTouchForm(payload(**{field: "x" * 301}))

    assert not form.is_valid()
    assert field in form.errors


def test_message_length_is_limited():
    form = GetInTouchForm(payload(message="x" * (MESSAGE_MAX_LENGTH + 1)))

    assert not form.is_valid()
    assert "message" in form.errors


def test_whitespace_only_input_is_rejected():
    form = GetInTouchForm(payload(name="   ", subject="  ", message=" "))

    assert not form.is_valid()
    assert {"name", "subject", "message"} <= set(form.errors)


def test_text_fields_are_trimmed():
    form = GetInTouchForm(payload(name="  hong  ", subject=" hi "))

    assert form.is_valid(), form.errors
    assert form.cleaned_data["name"] == "hong"
    assert form.cleaned_data["subject"] == "hi"


@pytest.mark.parametrize(
    "email", ["not-an-email", "missing@domain", "@example.com"]
)
def test_malformed_emails_are_rejected(email):
    form = GetInTouchForm(payload(emailfrom=email))

    assert not form.is_valid()
    assert "emailfrom" in form.errors


@pytest.mark.parametrize(
    "email", ["a@test.com", "a@mytest.co.kr", "a@TEST.io"]
)
def test_test_domains_are_rejected(email):
    form = GetInTouchForm(payload(emailfrom=email))

    assert not form.is_valid()
    assert "emailfrom" in form.errors


@override_settings(EMAIL_DNS_VALIDATION=True)
def test_dns_failure_does_not_block_a_valid_address():
    """DNS 조회 실패는 '검증 불가'이지 '잘못된 주소'가 아니다."""
    from validate_email.exceptions import DNSTimeoutError

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            "portfolio.forms.validate_email",
            lambda **kwargs: (_ for _ in ()).throw(DNSTimeoutError()),
        )
        form = GetInTouchForm(payload())

        assert form.is_valid(), form.errors


@override_settings(EMAIL_DNS_VALIDATION=True)
def test_domain_without_mx_record_is_rejected():
    from validate_email.exceptions import NoMXError

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            "portfolio.forms.validate_email",
            lambda **kwargs: (_ for _ in ()).throw(NoMXError()),
        )
        form = GetInTouchForm(payload())

        assert not form.is_valid()
        assert "emailfrom" in form.errors


@override_settings(EMAIL_DNS_VALIDATION=True)
def test_falsy_validation_result_is_rejected():
    """validate_email이 예외 없이 False를 돌려주는 경로."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("portfolio.forms.validate_email", lambda **kwargs: False)
        form = GetInTouchForm(payload())

        assert not form.is_valid()
        assert "emailfrom" in form.errors


@override_settings(EMAIL_DNS_VALIDATION=True)
def test_dns_validation_runs_when_enabled():
    calls = {}

    def fake_validate(**kwargs):
        calls.update(kwargs)
        return True

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("portfolio.forms.validate_email", fake_validate)
        assert GetInTouchForm(payload()).is_valid()

    assert calls["check_dns"] is True
    assert calls["check_smtp"] is False
    assert calls["email_address"] == "hong@example.com"

import logging

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from validate_email import validate_email
from validate_email.exceptions import (
    DNSConfigurationError,
    DNSTimeoutError,
    Error,
    NoNameserverError,
)

from .validators import PHONE_NUMBER_MAX_LENGTH, korean_mobile_number_validator

logger = logging.getLogger(getattr(settings, "PORTFOLIO_LOGGER", "django"))

NAME_MAX_LENGTH = 300
SUBJECT_MAX_LENGTH = 300
EMAIL_MAX_LENGTH = 128
MESSAGE_MAX_LENGTH = 5000

INVALID_EMAIL_MESSAGE = _(
    "The email failed validation. Please enter the email address you actually use"
)

# DNS 조회 자체가 불가능한 경우. 이메일이 틀린 것이 아니라 검증을 못 한 것이므로
# 정상 사용자를 막지 않고 통과시킨다.
DNS_INFRASTRUCTURE_ERRORS = (
    DNSTimeoutError,
    DNSConfigurationError,
    NoNameserverError,
)


class GetInTouchForm(forms.Form):
    """포트폴리오 문의 폼.

    이전 구현은 뷰에서 request.POST를 직접 읽고 저장 전에 길이/형식 검증을 하지
    않아, 16자를 초과한 전화번호가 DB insert까지 도달해 DataError를 냈다.
    입력 정책을 이 폼 한 곳에 모아 모델 컬럼 제약과 일치시킨다.
    """

    name = forms.CharField(
        max_length=NAME_MAX_LENGTH,
        strip=True,
        error_messages={"required": _("Name can't be empty.")},
    )
    emailfrom = forms.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        error_messages={"required": _("email can't be empty.")},
    )
    number = forms.CharField(
        required=False,
        max_length=PHONE_NUMBER_MAX_LENGTH,
        strip=True,
        validators=[korean_mobile_number_validator],
    )
    subject = forms.CharField(
        max_length=SUBJECT_MAX_LENGTH,
        strip=True,
        error_messages={"required": _("subject can't be empty.")},
    )
    message = forms.CharField(
        max_length=MESSAGE_MAX_LENGTH,
        strip=True,
        widget=forms.Textarea,
        error_messages={"required": _("message can't be empty.")},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # captcha는 설정으로 켠 환경에서만 붙인다. RECAPTCHA 키가 없는 환경과
        # 외부 호출을 하면 안 되는 테스트에서 폼을 그대로 쓸 수 있어야 한다.
        # 필드를 클래스 속성으로 두면 import 시점에 키를 요구하므로 여기서 만든다.
        if getattr(settings, "CONTACT_FORM_CAPTCHA", False):
            from captcha.fields import ReCaptchaField

            self.fields["captcha"] = ReCaptchaField(
                error_messages={
                    "required": _("Please confirm that you are not a robot."),
                }
            )

    def clean_emailfrom(self) -> str:
        email = self.cleaned_data["emailfrom"]
        _local, domain = email.rsplit("@", 1)

        if "test" in domain.lower():
            raise forms.ValidationError(
                _("Incorrect domain. Please enter the domain you actually use.")
            )

        if not getattr(settings, "EMAIL_DNS_VALIDATION", True):
            return email

        try:
            is_valid = validate_email(
                email_address=email,
                check_format=True,  # 이메일 형식 검증
                check_blacklist=True,  # 블랙리스트 도메인 검증
                check_dns=True,  # DNS MX 레코드 검증
                dns_timeout=getattr(
                    settings, "EMAIL_DNS_VALIDATION_TIMEOUT", 10
                ),
                check_smtp=False,  # SMTP 연결 통한 실제 이메일 존재 여부 검증
                smtp_timeout=10,
                smtp_helo_host=settings.SMTP_HOST,
                smtp_from_address=settings.SMTP_FROM_ADDRESS,
                smtp_skip_tls=False,
                smtp_debug=False,
            )
        except DNS_INFRASTRUCTURE_ERRORS as error:
            logger.warning(
                "email dns validation unavailable: %s",
                error,
                extra={"error": str(error)},
            )
            return email
        except (Error, ValueError) as error:
            # 이전 구현은 이 경로에서 초기화되지 않은 is_valid를 반환해
            # UnboundLocalError가 날 수 있었다.
            logger.debug(
                "email validation failed: %s", error, extra={"error": str(error)}
            )
            raise forms.ValidationError(INVALID_EMAIL_MESSAGE)

        if not is_valid:
            raise forms.ValidationError(INVALID_EMAIL_MESSAGE)

        return email

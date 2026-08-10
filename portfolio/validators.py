from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# 국내 휴대폰 번호. 하이픈은 있어도 되고 없어도 된다.
# 최대 길이는 모델 컬럼(varchar 16)과 폼에서 동일하게 강제한다.
KOREAN_MOBILE_NUMBER_REGEX = r"^01[016789]?-?[0-9]{3,4}-?[0-9]{4}$"

PHONE_NUMBER_MAX_LENGTH = 16

korean_mobile_number_validator = RegexValidator(
    regex=KOREAN_MOBILE_NUMBER_REGEX,
    message=_(
        "Enter a valid mobile number. Example: 010-1234-5678 or 01012345678."
    ),
)

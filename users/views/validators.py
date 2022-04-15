from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..models import UserVerification


'''
필드의 유효성 검증 필터는 반드시 __call__ 메소드를 오버라이드 해줘야 합니다.
이 메소드는 인스턴스를 invoke 연산자(소괄호)로 호출시 실행하는 함수입니다.
폼의 필드는 유효성을 검증할 때 필드에 정의된 default_validators 리스트의 각 원소들을
입력된 값을 전달하여 함수처럼 호출합니다.

* 그렇기 때문에 validators=(EmailField.default_validators + [RegisteredEmailValidator()]) 라고
필터에 인스턴스를 추가했지만 내부적으로 for validator in default_validators: validator(email) 이런 식으로
호출이 가능합니다.

원래 클래스의 인스턴스는 invoke 연산자로 호출이 불가능합니다.
파이썬에서는 함수도 객체(인스턴스)인데, __call__ 메소드가 구현되어 있다고 생각하시면 됩니다.
'''


class RegisteredEmailValidator:
    user_model = get_user_model()
    code = 'invalid'

    def __call__(self, email):
        try:
            user = self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
            return
        else:
            if user.verified is False:
                raise ValidationError('Get your email verified.', code=self.code)
            if user.is_active:
                raise ValidationError('Already certified.', code=self.code)

        return


class LoginVerificationEmailValidator:
    user_model = get_user_model()
    code = 'invalid'

    def __call__(self, email):
        try:
            user = self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
            raise ValidationError('You must register first.', code=self.code)
        else:
            if user.verified is not True:
                raise ValidationError('You have to get email verification first', code=self.code)

        return


class ResendVerificationEmailValidator:
    user_model = get_user_model()
    code = 'invalid'

    def __call__(self, email):
        try:
            user = self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
            raise ValidationError('You must register first.', code=self.code)
        else:
            if user.verified is True:
                raise ValidationError('Your email verification is successfully finished', code=self.code)

        return


class ResetPasswordEmailValidator:
    user_model = get_user_model()
    code = 'invalid'

    def __call__(self, email):
        try:
            self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
            raise ValidationError('Your email information does not exist.', code=self.code)

        return
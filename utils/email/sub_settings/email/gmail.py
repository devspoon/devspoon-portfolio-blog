from decouple import config

# Email 전송 by personal gmail account
# 메일을 호스트하는 서버
EMAIL_HOST = config('EMAIL_HOST')
# gmail과의 통신하는 포트
EMAIL_PORT = config('EMAIL_PORT')
# 발신할 이메일
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# 발신할 메일의 비밀번호
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# TLS 보안 방법
EMAIL_USE_TLS = True
# 사이트와 관련한 자동응답을 받을 이메일 주소
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
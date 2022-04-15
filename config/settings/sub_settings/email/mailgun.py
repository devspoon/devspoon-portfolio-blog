# 2. 하루 300건[월 9,000건] 이상이라면 Mailgun Flex 플랜 (1000건당 $0.80 종량제)

# 모니터링 : 현재 보낸 메일 수가 300개가 넘고, 1주일 내 보내야 하는 시스템 메일이 평균 50%~70%가 넘어가면 
# mailgun으로 이전, 현재 보낸 메일 수가 2만건 이상이 되면 경고 메시지 전송 후 관리자가 메일 서버 선택 
# (이벤트로 인한 일시적인건지, 시스템 전송량이 50% ~70% 평균 전송량을 가지는지 확인 필요)

# pip install django-mailgun-provider or pip install django-mailgun-mime

from decouple import config

EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = config('MAILGUN_ACCESS_KEY')
MAILGUN_SERVER_NAME = config('MAILGUN_SERVER_NAME')
DEFAULT_FROM_EMAIL = config('MAILGUN_DEFAULT_FROM_EMAIL')

MAIL_VENDOR = 'mailgun'
# Agent Handoff

## 현재 상태

- `docs/error`에 Sentry export 5개가 있다.
- `docs/error`는 현재 git 기준 미추적 상태로 보인다.
- 이 문서 세트는 `docs/ai-docs`에 새로 작성되었다.
- 코드 변경은 아직 하지 않았다.

## 주요 코드 위치

- 통계 미들웨어: `custom_middlewares/middlewares/statistics.py`
- 통계 모델: `custom_middlewares/models.py`
- 통계 admin 등록: `home/admin/default_admin.py`
- 문의 모델: `portfolio/models.py`
- 문의 뷰: `portfolio/views.py`
- 문의 템플릿: `templates/portfolio/portfolio.html`
- 메일 스레드 발송: `utils/email/async_send_email.py`
- 공통 middleware 설정: `config/settings/base.py`
- 운영 `ALLOWED_HOSTS`: `config/settings/prod.py`

## 다음 에이전트가 바로 확인할 것

1. 운영 nginx 설정 파일은 이 저장소에 없다. 배포 환경에서 별도로 확인해야 한다.
2. Django 마이그레이션 디렉터리가 현재 검색에서 보이지 않았다. 실제 migration 정책을 먼저 확인한다.
3. `custom_middlewares.models`의 통계 모델은 `Meta.app_label = "home"`을 사용한다. migration 생성 전 Django app label과 migration module을 반드시 검증한다.
4. `GetInTouchView.post()`에는 첫 번째 return 이후 dead code가 여러 번 반복된다. 기능 수정 시 함께 정리한다.
5. `utils/email/async_send_email.py`는 호출자에게 발송 결과를 반환하지 않는다. 메일 실패 처리 설계 시 이 제약을 반영한다.

## 구현 순서 권장

1. nginx 1차 차단 적용
2. Django 2차 차단 미들웨어 추가
3. 통계 중복 데이터 정리
4. 통계 모델/미들웨어 구조 개선
5. 문의 폼 검증 개선
6. 메일 실패 처리 개선
7. Sentry 필터와 테스트 보강

## 열려 있는 결정

- nginx 차단 응답: `444` 유지 또는 `404`/`403` 대체
- 전화번호 입력 정책: 국내 휴대폰만 허용 또는 국제 번호 허용
- 통계의 봇 처리: 제외, 별도 bot 카운트, 현행 유지
- `GetInTouchLog.state` 의미: 접수 성공인지 메일 발송 성공인지
- 메일 비동기 처리: 현행 스레드 유지, Celery 전환, 동기 발송 선택지 추가

## 검증 명령 후보

```bash
python manage.py check --settings=config.settings.dev
python manage.py test home.tests.test_error --settings=config.settings.test
python manage.py test portfolio --settings=config.settings.test
```

환경변수와 DB 의존성이 있으므로 로컬에서 바로 실행되지 않을 수 있다. 실패 시 누락된 환경변수와 DB 연결 설정을 먼저 확인한다.

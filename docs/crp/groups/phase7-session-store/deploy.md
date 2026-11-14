# 배포 절차 — phase7 세션 DB 저장

> 실행은 사용자가 한다. 순서를 지키면 로그인한 사용자가 로그아웃되지 않는다.

## 배포 전
1. DB 백업(평소 절차).
2. 운영 DB에 세션 테이블이 있는지 확인한다(없으면 3단계 `migrate`가 만든다).
   ```sh
   python manage.py showmigrations sessions --settings=config.settings.prod
   ```
   `[X] 0001_initial`이면 이미 있다.

## 배포
3. 코드를 배포하고 평소처럼 `migrate`를 실행한다. 이쪽 앱의 새 마이그레이션은 없다. 세션 테이블이 없을 때만 Django 자체 마이그레이션이 적용된다.
4. **배포 직후 바로** Redis에 있던 세션을 DB로 옮긴다. 이 명령을 실행하기 전까지는 기존 로그인 사용자가 로그아웃된 것처럼 보인다. 옮긴 뒤에는 같은 세션 그대로 로그인 상태로 돌아온다.
   ```sh
   python manage.py move_sessions --dry-run --settings=config.settings.prod   # 옮길 개수만 확인
   python manage.py move_sessions --settings=config.settings.prod
   ```
   - 여러 번 실행해도 안전하다(이미 옮긴 세션은 건너뛰고, Redis에 남은 세션 키만 지운다).
   - 세션이 아닌 캐시 키는 건드리지 않는다.
   - 옮긴 세션의 수명은 2주로 다시 정해진다(요청할 때마다 연장).

## 배포 후
5. 만료 세션 정리 일정을 등록한다(admin → Periodic tasks → 추가).
   - Task: `users.tasks.clear_expired_sessions`
   - Interval/Crontab: 하루 한 번(예: 새벽 4시)
   - Celery worker와 beat가 떠 있어야 실행된다. beat를 운영하지 않으면 서버 cron에 `python manage.py clearsessions --settings=config.settings.prod`를 하루 한 번 등록한다.
6. 며칠 뒤 세션 행 수가 계속 늘기만 하지 않는지 확인한다.
   ```sh
   python manage.py shell --settings=config.settings.prod -c "from django.contrib.sessions.models import Session; print(Session.objects.count())"
   ```

## 되돌리기
- 코드를 이전 버전으로 되돌리면 세션은 다시 Redis에서 찾으므로 그 시점에 로그인한 사용자는 한 번 로그아웃된다. DB의 `django_session` 행은 지워도 되고 남겨도 된다.

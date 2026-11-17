# 배포 절차 — phase7 세션 DB 저장

> 실행은 사용자가 한다. 로그인한 사용자는 배포 순간에도, 그 뒤에도 로그아웃되지 않는다.

## 어떻게 로그아웃 없이 넘어가는가
- 이번 배포의 세션 엔진은 **전환용**(`common.core.session_transition`)이다. 세션을 DB에서 먼저 찾고, 없으면 옛 위치(Redis)를 한 번 본다. 있으면 같은 세션 번호로 DB에 옮기고 그대로 로그인시킨다.
- 그래서 배포 직후부터 방문하는 사용자는 그 요청에서 바로 옮겨진다. 방문하지 않은 사용자의 세션은 아래 4단계 `move_sessions`가 한 번에 옮긴다.
- (정정) 전환용 엔진이 없을 때는, 배포 뒤 `move_sessions` 전에 방문한 사용자의 쿠키를 Django가 지워 다시 로그인해야 했다(실측). 이전 판 문서의 "옮기면 다시 로그인 상태로 돌아온다"는 그 사용자들에게는 맞지 않았다.

## 배포 전
1. DB 백업(평소 절차).
2. 운영 DB에 세션 테이블이 있는지 확인한다(없으면 3단계 `migrate`가 만든다).
   ```sh
   python manage.py showmigrations sessions --settings=config.settings.prod
   ```
   `[X] 0001_initial`이면 이미 있다.

## 배포
3. 코드를 배포하고 평소처럼 `migrate`를 실행한다. 이쪽 앱의 새 마이그레이션은 없다. 세션 테이블이 없을 때만 Django 자체 마이그레이션이 적용된다.
4. 배포 뒤 편한 때에(급하지 않다) 아직 방문하지 않은 사용자의 세션을 한 번에 옮긴다.
   ```sh
   python manage.py move_sessions --dry-run --settings=config.settings.prod   # 옮길 개수만 확인
   python manage.py move_sessions --settings=config.settings.prod
   python manage.py move_sessions --dry-run --settings=config.settings.prod   # 0개면 끝
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

## 브랜치와 배포 순서
| 브랜치 | 세션 엔진 | 언제 |
|---|---|---|
| `crp/phase7-session-store` (`258c7ed`) | 전환용(`common.core.session_transition`) | **첫 배포 권장.** 배포 순간 방문자도 로그아웃되지 않는다 |
| `crp/phase7b-session-engine-cleanup` | `django.contrib.sessions.backends.db` | 첫 배포 뒤 `move_sessions --dry-run`이 0개를 보고한 다음 배포 |

> 엔진 없이 곧바로 `crp/phase7b-session-engine-cleanup`을 첫 배포로 반영하면, 배포와 `move_sessions` 사이에 방문한 사용자는 쿠키가 지워져 다시 로그인해야 한다. 그 경우 4단계 `move_sessions`를 **배포 직후 곧바로** 실행한다.

## 전환용 엔진 걷어내기 (다음 배포) — `crp/phase7b-session-engine-cleanup`에서 완료
7. 4단계 `move_sessions --dry-run`이 0개를 보고한 뒤라면 언제든:
   - `config/settings/{dev,stage,prod,test}.py`의 `SESSION_ENGINE`을 `"django.contrib.sessions.backends.db"`로 바꾼다.
   - `common/core/session_transition.py`와, 그 엔진만 확인하는 테스트(`common/test_phase7_sessions.py`의 "전환 빈틈" 묶음)를 지운다.
   - `move_sessions` 명령은 남겨 두어도 해가 없다(옮길 것이 없으면 0개).

## 되돌리기
- 코드를 이전 버전으로 되돌리면 세션은 다시 Redis에서 찾는다. 이미 DB로 옮긴 사용자는 그 시점에 한 번 로그아웃된다. DB의 `django_session` 행은 지워도 되고 남겨도 된다.

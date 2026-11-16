# Design Baseline — phase7-session-store

> 상위: 원래 검토 H11 "세션 저장소 분리". 브랜치 `crp/phase7-session-store`(6단계 `394c23c` 위).

## 0. 질의 수준
보통 — 운영 영향(로그아웃, 세션 수명, 정리 방식)은 사용자 결정.

## 1. 현재 상태 (조사 결과)
| 항목 | 값 | 근거 |
|---|---|---|
| 세션 엔진 | `django.contrib.sessions.backends.cache`, `SESSION_CACHE_ALIAS = "default"` | dev·stage·prod·test 설정 |
| 저장 위치 | 일반 캐시와 같은 Redis DB·같은 `KEY_PREFIX` | 설정 |
| 서버 쪽 수명 | **2147483647초(약 68년)**. `SESSION_COOKIE_AGE = 2147483647` + `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` | 실측 |
| 생성 시점 | 비로그인 일반 화면 GET은 세션을 만들지 않음. 로그인 때 생성 | 실측 |
| 저장 빈도 | `SESSION_SAVE_EVERY_REQUEST = True` — 세션이 있는 요청(로그인 사용자)마다 저장 | base 설정 |
| DB 세션 읽기 | Django `db` 백엔드는 `Session.objects.get(...)`으로 읽어 **이 프로젝트 라우터에 의해 replica로 간다**(쓰기는 default) | `django/contrib/sessions/backends/db.py:34` |
| 세션 테이블 | `django.contrib.sessions`가 이미 설치돼 dev DB에 `django_session` 있음(Django 자체 마이그레이션) | dev DB 확인 |
| 주기 작업 | Celery beat `DatabaseScheduler` — 작업은 `@shared_task`, 일정은 admin의 PeriodicTask 행. dev에는 등록된 일정 없음, 운영은 확인 불가 | `config/settings/*`, `users/tasks.py` |

## 2. 요청 기록
| Req-ID | 날짜 | 요청(원문 요약) | 도출된 요구사항 | 상태 | 연결 |
|---|---|---|---|---|---|
| REQ-001 | 2026-11-14 | "진행해줘"(7단계 세션 저장소 분리) | 세션을 일반 캐시와 분리 | Active | ADR-001~006 |
| REQ-004 | 2026-11-14 | "권장하는 방법으로 진행해줘" | 설계 v0.2 승인: D1-A(`db` 백엔드)·D2-A(`move_sessions`)·D3-A(2주, 요청마다 연장)·D4-A(Celery 정리 작업 + admin 일정 등록) | Active | ADR-001~006 |
| REQ-005 | 2026-11-16 | "3으로 진행해줘"(전환 빈틈을 임시 대체 세션 엔진으로 제거) | 배포 순간부터 `move_sessions` 실행 전까지 방문한 사용자도 로그아웃되지 않는다 | Active | ADR-007 |
| REQ-006 | 2026-11-16 | "승인한다. 진행해줘" | 설계 v0.3(ADR-007)·계획 승인 | Active | ADR-007 |
| REQ-002 | 2026-11-14 | 모든 작업은 설계 및 작업 계획 후 실행 | 승인 전 코드 변경 없음 | Active | — |
| REQ-003 | 2026-11-14 | "세션 정보를 db에 저장하는 방식으로 다시 고려해줘" | 세션을 DB에 저장하는 설계로 다시 짠다(v0.1 Redis DB 분리안 대체) | Active | ADR-001~006 |

## 3. 설계 결정 기록 (ADR)
| ADR-ID | 결정 | 근거 | 상태 | supersedes |
|---|---|---|---|---|
| ADR-001 | (D1) 세션 엔진을 DB로: 권장 `django.contrib.sessions.backends.db`. 대안 `cached_db`(읽기는 캐시 먼저, 저장은 DB+캐시) | Redis 비우기·재시작·메모리 축출과 무관하게 로그인이 유지된다(v0.1 Redis 분리안이 못 막던 R-001 해소). Redis DB 번호 확인(옛 D1)이 필요 없다 | Accepted | v0.1 ADR-001 |
| ADR-002 | 라우터: `sessions` 앱 모델은 읽기도 항상 `default` | 그대로 두면 로그인(POST, default에 저장) 직후 GET이 replica에서 세션을 찾다가 지연이 있으면 로그아웃된 것처럼 보인다. 5단계 "항상 빈 replica" 테스트로 확인 | Accepted | v0.1 ADR-004 |
| ADR-003 | (D3) 세션 수명 2주, 요청마다 연장(`SESSION_COOKIE_AGE = 1209600`, `SESSION_SAVE_EVERY_REQUEST` 유지) | DB 행은 만료돼야 정리할 수 있다. 68년이면 행이 영원히 남는다 | Accepted | — |
| ADR-004 | (D4) 만료 행 정리: Django 내장 `clearsessions` | DB 세션은 만료돼도 행이 자동으로 지워지지 않는다 | Accepted | — |
| ADR-005 | (D2) 전환 방법: 기존 Redis 세션을 DB 행으로 옮기는 `move_sessions` 명령(로그아웃 없음) 또는 강제 로그아웃 공지 | — | Accepted | — |
| ADR-006 | 스키마: 새 마이그레이션 없음. `django_session`은 Django 자체 마이그레이션으로 이미 있다(운영은 배포 때 `migrate`로 확인) | 이쪽 앱 모델 변경 없음 | Accepted | — |

| ADR-007 | 2026-11-16 | 전환용 세션 엔진 `common/core/session_transition.py`. Django `db` 엔진을 상속하고 `load()`만 덮어쓴다: DB에서 못 찾았고 쿠키에 세션 번호가 있으면, 옛 위치(`default` 캐시의 `django.contrib.sessions.cache<번호>`)를 한 번 본다. 있으면 같은 번호로 DB 행을 만들고 Redis 키를 지운 뒤 그 내용으로 로그인시킨다. 같은 번호로 동시에 두 요청이 와서 이미 행이 생겼으면(`CreateError`) 그대로 쓴다. 설정 4곳의 `SESSION_ENGINE`을 이 엔진으로. 전환이 끝나면(`move_sessions`로 남은 세션까지 옮긴 뒤) 다음 배포에서 `django.contrib.sessions.backends.db`로 되돌리고 파일을 지운다 | 실측: 배포 뒤 `move_sessions` 전에 방문하면 Django가 세션을 못 찾아 쿠키를 지워, 명령을 실행해도 다시 로그인해야 했다. 배포 사이에 명령을 끼우는 방법(②)은 배포 yml 변경이 필요해 범위 밖. 비용: DB에 없는 쿠키(만료·가짜)가 올 때마다 Redis GET 1회 | Accepted | — |

## 4. 불가침 제약
- C-1: 기존 테스트 전부 통과. C-2: 이쪽 앱 스키마 변경 없음. C-3: 인프라(배포 yml, secrets, 서버 cron, Redis·DB 서버 설정) 변경 없음. C-4: push 안 함, 운영 명령 실행 안 함(사용자가 배포 문서대로).

## 5. 변경 이력
- v0.1 (2026-11-14): 최초 작성(같은 Redis 안 DB 번호 분리안).
- v0.2 (2026-11-14): REQ-003으로 DB 저장 방식으로 재설계. v0.1 ADR-001·004 대체.
- v0.3 (2026-11-16): REQ-005, ADR-007(전환 빈틈 제거). `deploy.md`의 "옮기면 다시 로그인 상태로 돌아온다" 문장이 실측과 달라 정정 대상(F-004).

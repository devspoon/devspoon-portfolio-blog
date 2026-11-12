# Design Baseline — phase2-deps-upgrade (기준 설계 문서)

> 이 그룹의 요구사항·설계 결정의 단일 기준. append-only.

## 0. 질의 수준 (Autonomy Level)

- [x] **적극(Thorough)**
- [ ] 보통(Balanced)
- [ ] 간략(Lean)

선택: **적극** · 선택일: 2026-11-12 · 변경 이력: 없음

> 사용자 규칙: 설계·작업 계획 승인 후 실행. 실행 중 계획 밖 수정이 필요하면 고치기 전에 멈추고 묻는다. 커밋만 하고 push·병합·배포는 하지 않는다. 인프라(nginx·gunicorn·서버)는 고려하지 않는다.

## 1. 목적 / 배경

모든 Python 패키지를 최신으로 올린다(사용자 허용, 2026-11-12). 캐시 재설계(3단계)와 그 뒤 작업을 오래된 의존성 위에서 했다가 다시 고치지 않도록 이 단계를 먼저 한다. 1단계에서 갖춘 회귀 테스트(210개)와 runserver 검증 환경(WSL Redis·PostgreSQL)을 안전망으로 쓴다.

## 2. 요구사항 레지스터

| Req-ID | 날짜 | 요청(원문 요약) | 도출된 요구사항 | 상태 | 연결 |
|---|---|---|---|---|---|
| REQ-001 | 2026-11-12 | "모든 패키지들을 최신화 하는 것을 허용한다" → U1~U3 "권장안대로 진행해줘" | 최상위 의존성 전부를 의존성 해석이 허용하는 최신으로 올린다. Python 최소 버전을 3.12로, CI(`testing.yml`)도 3.12로. 쓰지 않는 `django-nose` 제거, `isort`는 dev 그룹으로. | Active | ADR-003~008 |
| REQ-002 | 2026-11-12 | "django는 5.2 LTS로 정의해서 설계 및 작업계획을 업데이트해줘" | Django 목표를 5.2 LTS로 고정한다(`~5.2`, 6.x로 올라가지 않음). 서드파티는 Django 5.2에서 해석되는 최신으로 올린다. Python 3.12·CI 3.12 결정(U2)은 유지한다. | Active | ADR-007, ADR-008 |

## 3. 설계 결정 기록 (ADR)

| ADR-ID | 날짜 | 결정 | 근거 | 상태 | supersedes |
|---|---|---|---|---|---|
| ADR-001 | 2026-11-12 | **Django 목표는 6.0.x(현재 6.0.10)** 로 한다(U1 수정 제안). | 조사 결과 `django-celery-beat` 최신(2.9.0)이 `Django <6.1`을 요구한다. 이 패키지는 dev·stage·prod의 `INSTALLED_APPS`와 `CELERY_BEAT_SCHEDULER`(DB 스케줄러)로 쓰인다. 6.0은 이 조건에서 해석 가능한 최신이다. celery-beat가 6.1을 지원하면 6.1로 올린다(R-002). | Superseded(ADR-007) | U1(6.1) |
| ADR-002 | 2026-11-12 | 4.2 → **5.2 LTS → 6.0** 순서로 한 단계씩 올린다. 5.2에서 `RemovedInDjango60Warning`을 오류로 바꿔 테스트를 돌려 6.0에서 사라질 사용처를 먼저 고친다. | Django 공식 권장 업그레이드 경로. 문제가 생기면 5.2 LTS에서 멈출 수 있다. | Superseded(ADR-008) | — |
| ADR-003 | 2026-11-12 | 서드파티 메이저 업그레이드는 Django 단계와 분리해 묶음별로 한다. 단, Django 단계에서 의존성 해석상 함께 올라가야 하는 패키지는 그 단계에서 올리고 기록한다. | 실패 원인을 한 묶음 안으로 좁히기 위해. | Accepted | — |
| ADR-004 | 2026-11-12 | `common/mixin/admin/trim_html_tags.py`의 인자 없는 `format_html(x)` 2곳을 주석의 의도대로 `strip_tags(x)`로 바꾼다. | Django 6.0에서 인자 없는 `format_html`이 제거된다. 현재 동작은 제목 HTML을 이스케이프 없이 admin에 출력하는 것이라 저장된 XSS 여지도 있다. 주석의 의도는 태그 제거다. | Accepted | — |
| ADR-005 | 2026-11-12 | django-recaptcha 4는 import 경로가 `captcha` → `django_recaptcha`로 바뀌므로 설정 4개·코드 2개·테스트 1개의 경로와 system check ID를 함께 바꾼다. | 패키지 이름 변경에 따른 필수 수정. | Accepted | — |
| ADR-006 | 2026-11-12 | 우리 앱의 모델 스키마는 바꾸지 않는다. 업그레이드 전후 `makemigrations --check --dry-run`이 우리 앱에 대해 "No changes"여야 한다. 서드파티 앱의 migration은 그대로 적용한다. | migration 파일을 저장소에 두지 않으므로(서버에서 생성) 업그레이드가 우리 스키마를 바꾸면 운영에서 예기치 않은 migration이 생긴다. `DEFAULT_AUTO_FIELD`는 이미 `BigAutoField`라 Django 6.0 기본값 변경의 영향이 없다. | Accepted | — |
| ADR-007 | 2026-11-12 | **Django 목표는 5.2 LTS**로 하고 조건을 `~5.2`(5.2.x만)로 둔다. 현재 해석 결과 5.2.19. | 사용자 결정(REQ-002). 5.2는 LTS라 2028년 4월까지 보안 지원을 받는다. 임시 사본 해석에서 `~5.2` + 서드파티 최신 메이저(allauth 65.22, recaptcha 4.1, django-redis 7.0, sentry-sdk 2.74, debug-toolbar 8.0, silk 5.6, celery-beat 2.9, celery 5.7)가 모두 해석됨을 확인했다. | Accepted | ADR-001 |
| ADR-008 | 2026-11-12 | 4.2 LTS → 5.2 LTS로 **한 번에** 올린다. 올리기 전에 4.2에서 `RemovedInDjango50Warning`·`RemovedInDjango51Warning`을 오류로 바꿔 pytest를 돌려 5.x에서 사라지는 사용처를 먼저 고친다. 5.2로 올린 뒤에는 `RemovedInDjango60Warning`을 오류로 바꿔 pytest가 통과하게 해 둔다(향후 6.x 이전 준비). | LTS→LTS 직행은 Django가 지원하는 경로이고, 중간 비 LTS(5.0·5.1)를 거칠 이유가 없다. 6.0 경고 정리는 F-001(admin XSS 여지)과 겹쳐 비용이 작다. 이 정리가 C-3 범위를 넘으면 기록만 하고 멈춘다. | Accepted | ADR-002 |

## 4. 불가침 제약

- C-1: 기존 테스트 전부(현재 210 passed / 1 skipped)가 각 하위 단계 후에도 통과한다. 테스트를 지우거나 skip해서 통과시키지 않는다. — REQ-001
- C-2: 우리 앱 스키마 변경 없음(ADR-006). — REQ-001
- C-3: 사용자에게 보이는 동작 변경은 이 문서에 적은 것만 허용한다(ADR-004, Django 5.0의 사이트맵 https 기본값. Django 5.2는 `forms.URLField` 기본 scheme을 http로 유지하므로 해당 없음). 그 밖의 변경이 필요하면 멈추고 묻는다. — REQ-001
- C-4: 인프라 파일(`stage-ver-deploy.yml`·`test-ver-deploy.yml`)은 바꾸지 않는다. `testing.yml`은 Python 버전만 바꾼다(U2). — REQ-001, phase1 REQ-003
- C-5: 커밋만 하고 push·병합하지 않는다. PR을 쓰지 않는다. — phase1 REQ-002
- C-6: WSL의 다른 컨테이너와 로컬 DB 백업은 건드리지 않는다. — phase1 C-7

## 5. 변경 이력
- v0.1 (2026-11-12): 최초 작성. 설계만, 패키지는 아직 바꾸지 않음.
- v0.2 (2026-11-12): REQ-002. Django 목표를 5.2 LTS로(ADR-007이 ADR-001 대체), 4.2→5.2 직행(ADR-008이 ADR-002 대체). 2-c(Django 6.0) 단계 삭제.

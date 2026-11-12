# Checklist — phase2-deps-upgrade (개선 항목 추적판)

## Round 0 — 2026-11-12 (설계)
- [x] 이번 요청을 design-baseline §2에 기록(REQ-001) + 이전 요구 충돌 확인(phase1 불가침 제약 승계)
- [x] 업그레이드 대상·해석 가능 여부 조사, Django 릴리스 노트 대조
- [x] 계약·불변식·인수 기준 작성(charter v0.1)
- [x] 설계 수정(REQ-002): Django 목표 5.2 LTS — ADR-007·008
- [x] **사용자 설계 승인**(ADR-003~008 Accepted, 2026-11-12)

## Round 1 — (승인 후)
- [x] 0 기준선 확인 — 우리 앱 No changes, 210 passed, runserver 점검표 통과(로컬 DB에 더미 SocialApp 3개 등록 후)
- [x] 2-a 정리·저위험 — INV-1~4 통과
- [x] 2-b Django 5.2 LTS — 4.2 경고 0건, 5.2.19로, INV-1~4 통과, F-001 Fixed. INV-5는 URLField 경고 1종(F-005) 결정 대기
- [x] 2-c ① django-redis 7.0.0·redis-py 8.1.0 — INV-1~4 통과, 캐시 키·TTL·세션 저장 확인
- [x] 2-c ② django-recaptcha 4.1.0 — INV-1~4 통과, F-002 Fixed, 가입 화면 캡차 위젯 확인
- [x] 2-c ③ django-allauth 65.22.0(socialaccount extras) — INV-1~4 통과, F-003 Fixed, 소셜 로그인 시작 redirect 확인
- [x] 2-c ④ sentry-sdk 2.74.0·debug-toolbar 8.0.0·extensions 4.1 — INV-1~4 통과. LoggingPanel 제거(라이브러리 요구), sentry `send_default_pii` 경고는 F-006 결정 대기
- [x] 2-c ⑤ imagekit 6.1.1·mptt 0.21.1·anymail 15.2·rangefilter 0.15.0·uvicorn 0.54.0 — INV-1~4 통과, mptt·rangefilter admin 200, 썸네일 생성 확인
- [x] 마무리: 최상위 outdated는 Django(5.2 고정)뿐, 하위 48개는 F-007. 불가침 제약 C-1~C-6 위반 없음. 판정 NOT CONVERGED(INV-5가 F-005 결정 대기)

## Round 2 — 2026-11-12 (결정 반영, REQ-003)
- [x] 요청 기록(REQ-003)과 결정 ADR-009~012
- [x] F-007 `poetry update` — INV-1~4 통과, 소셜 로그인 redirect·썸네일 생성(pillow 13)·sentry 초기화 확인
- [x] F-005 INV-5 — URLField 경고 1종만 예외로 212 passed
- [x] F-004 `requirements/dev.txt` 재생성 — pip dry-run exit 0
- [x] F-006 유지 — 잔여 위험 R-007
- [x] 판정 CONVERGED(Open Fix 0, INV-1~5 통과, 인수 기준 충족, 불가침 제약 위반 없음)

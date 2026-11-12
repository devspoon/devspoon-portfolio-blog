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
- [ ] 2-c ② django-recaptcha 4 — INV-1~4, F-002
- [ ] 2-c ③ django-allauth 65 — INV-1~4, F-003
- [ ] 2-c ④ sentry 2·debug-toolbar 8·extensions 4 — INV-1~4
- [ ] 2-c ⑤ imagekit·mptt·anymail·rangefilter·uvicorn — INV-1~4
- [ ] 마무리: outdated 목록 기록, 불가침 제약 C-1~C-6 위반 없음, 수렴 판정

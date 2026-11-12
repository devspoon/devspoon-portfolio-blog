# Checklist — phase2-deps-upgrade (개선 항목 추적판)

## Round 0 — 2026-11-12 (설계)
- [x] 이번 요청을 design-baseline §2에 기록(REQ-001) + 이전 요구 충돌 확인(phase1 불가침 제약 승계)
- [x] 업그레이드 대상·해석 가능 여부 조사, Django 릴리스 노트 대조
- [x] 계약·불변식·인수 기준 작성(charter v0.1)
- [ ] **사용자 설계 승인**(ADR-001~006, 특히 ADR-001의 Django 6.0 목표)

## Round 1 — (승인 후)
- [ ] 0 기준선 확인
- [ ] 2-a 정리·저위험 — INV-1~4
- [ ] 2-b Django 5.2 LTS — INV-1~5, F-001
- [ ] 2-c Django 6.0 — INV-1~4
- [ ] 2-d ① django-redis 7 — INV-1~4
- [ ] 2-d ② django-recaptcha 4 — INV-1~4, F-002
- [ ] 2-d ③ django-allauth 65 — INV-1~4, F-003
- [ ] 2-d ④ sentry 2·debug-toolbar 8·extensions 4 — INV-1~4
- [ ] 2-d ⑤ imagekit·mptt·anymail·rangefilter·uvicorn — INV-1~4
- [ ] 마무리: outdated 목록 기록, 불가침 제약 C-1~C-6 위반 없음, 수렴 판정

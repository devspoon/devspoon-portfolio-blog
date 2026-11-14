# Run Log — phase5-request-security

## 작업 계획 (승인됨, 실행됨)
| 순서 | 단계 | 확인 |
|---|---|---|
| 1 | 테스트 전용 `replica1`(빈 SQLite) + 라우터 적용 fixture. P-1·P-2 실패 테스트 | red |
| 2 | 라우터 `read_primary()`·미들웨어·`cached()`·댓글 목록 | green, 나머지 테스트 |
| 3 | P-3~P-6 실패 테스트(뷰 8종 parametrize) | red |
| 4 | `ReplyCreateMixin`·`ReplyUpdateMixin`, 뷰 8개 교체 | green |
| 5 | 전체 pytest·check·migration, runserver 점검표·SCAN | 게이트 |
| 6 | 문서·커밋(push 안 함) | — |

## 라운드 로그

### Round 1 — 2026-11-13 (브랜치 `crp/phase5-request-security`, 통합 `346c979` 위)
- **트리거:** 사용자 "승인한다"(D1-A·D2-A)
- **red:** 새 테스트 140개 중 123개 실패(replica 3, 생성 검증 64, 수정 검증 56), 정상 흐름 16개·GET replica 1개는 통과
- **실행 중 발견:** F-005(사용자 저장 시그널의 replica 읽기, 계획 밖이라 고치지 않고 질문), F-006(블로그 댓글 수정 GET 500, mixin 통합으로 함께 해소)
- **green:** 140 passed. fail-on-revert 7개(미들웨어, `cached()`, 댓글 목록, 같은 글 부모, 활성 글, 서버 depth, 수정 공백) 각각 테스트 실패 확인
- **게이트:** pytest **688 passed / 1 skipped**, check exit 0, 이쪽 앱 `makemigrations --check` No changes. runserver(dev 설정, 실제 라우터, PostgreSQL, 18765): 기존 점검표 전부 통과, 최상위 댓글 group 1→2, 대댓글 depth 99 → 1, 조작 입력(부모 `abc`·없는 부모·3001자·잘못된 JSON·공백 수정) 전부 400, `reply_count` = 행 수, 입력창 `maxlength` 2곳, 좋아요 동시 10개 0/0, Redis GET·SET만(SCAN 0), 서버 로그 500 0건
- **수렴 판정:** 계획 범위 `CONVERGED`(Open Fix는 사용자 결정 대기인 F-005 하나)
- **검사 범위의 한계:** 실제 replica 지연은 재현하지 않음(R-001). 브라우저에서 직접 누르지 않음. CI 미실행

### Round 2 — 2026-11-14 (F-005)
- **트리거:** 사용자 "작업 재개해줘" → F-005를 권장안 A로 진행(가정)
- **red:** `test_saving_a_user_checks_the_profile_on_the_primary` → `nickname` 중복 `IntegrityError`
- **green:** `on_save_user` 본문을 `read_primary()` 안에서. 되돌리면 실패, 복원하면 통과

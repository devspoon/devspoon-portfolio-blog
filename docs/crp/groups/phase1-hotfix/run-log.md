# Run Log — phase1-hotfix (라운드 로그 + 수렴 판정)

## 라운드 기록

### Round 0 — 2026-11-11 (base SHA: `5b647a4`)
- **트리거:** 사용자 요청("1단계 설계를 PR #9 병합 전에 미리 작성")
- **검수 범위:** 2026-11-11 전수 검수 결과 중 1단계 대상과, 설계 중 찾은 형제 버그(board 댓글 시그널, board 댓글 N+1)
- **GATE 통과:** 0 ■ 1 ■ 2 ■(계약 도출, 승인 대기) 3 □ 4 □ 5 □
- **신규 finding:** CRIT 4 · HIGH 1 · MED 2 · LOW 0 (F-001~F-007)
- **신규 Fix:** 7건(ledger F-001~F-007). 아직 구현하지 않음
- **수렴 판정:** `NOT CONVERGED`(설계 단계)
- **잔여 위험 변화:** R-001~R-004 등록

## 작업 계획 (승인 후 실행 — 순서 고정)

0. **선행 조건:** `docs/sentry-error-remediation-plan` 브랜치가 main에 로컬 병합되어야 한다(PR 미사용, C-6). 이 브랜치를 새 main 위로 다시 올린다(rebase). 테스트 기반(`conftest.py` 캐시 초기화)이 그 브랜치에 있기 때문이다.
1. **F-004·F-005 (C2):** 댓글 모델 8개를 parametrize한 삭제 테스트를 먼저 작성 → 실패(`DoesNotExist`) 확인 → 시그널 2개 수정 → 통과
2. **F-001·F-002 (C1 상세):** A가 먼저, B와 비로그인이 나중에 방문하는 테스트 + Redis 키 검사 작성 → 실패 확인 → 상세 뷰 8개 수정 → 통과
3. **F-003·F-006 (댓글 목록):** 요청자별 `user_auth` 테스트와 쿼리 수 테스트 작성 → 실패 확인 → 댓글 목록 뷰 8개 수정 → 통과
4. **F-007 (M2):** import 2줄 삭제 → 전체 테스트
5. **검수:** 인수 기준 전부 확인, fail-on-revert 기록, run-log Round 1 작성
6. **커밋:** 결함 묶음별로 커밋 4개(1~4단계). push는 하지 않는다

## 로컬 적용·검증 절차 (REQ-003: runserver + WSL 컨테이너, 인프라 제외)

1. 코드 반영 후 `pytest` 전체 실행
2. 키 정리(옛 캐시가 남아 있는 Redis일 때): 요청자별 값이 남은 키를 접두사 단위로 지운다. 세션이 같은 Redis DB에 있으므로 `FLUSHDB`는 쓰지 않는다.
   ```
   python manage.py shell -c "from django.core.cache import cache; [cache.delete_pattern(p) for p in ('blog:*:user_auth','blog:*:like_state','board:*:user_auth','blog:*Reply:*','board:*Reply:*')]"
   ```
   마지막 두 패턴은 첫 요청자 기준 `user_auth`가 들어 있는 댓글 목록 캐시다.
3. `runserver`(`config.settings.dev`)로 확인한다.
   - 작성자 로그인 창에서 상세 페이지를 먼저 열고, 시크릿 창(비로그인)과 다른 계정으로 같은 글을 연다 → 작성자에게만 수정·삭제 버튼
   - A가 좋아요를 누른 뒤 B로 열기 → B는 좋아요 안 눌린 상태
   - `redis-cli --scan --pattern "*user_auth*"` → 결과 없음
   - 댓글 작성 후 삭제 → 성공, 댓글 수 1 감소
   - A가 댓글 목록을 먼저 열고 B로 열기 → B에게 A 댓글의 수정·삭제 버튼 없음

## 심각도 추세
| Round | CRIT | HIGH | MED | LOW | 신규 Fix | 판정 |
|---|---|---|---|---|---|---|
| 0 | 4 | 1 | 2 | 0 | 7 | NOT CONVERGED(설계) |

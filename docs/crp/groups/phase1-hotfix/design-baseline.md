# Design Baseline — phase1-hotfix (기준 설계 문서)

> 이 그룹의 요구사항·설계 결정의 단일 기준. append-only — 항목은 지우지 않고 상태만 바꾼다.

## 0. 질의 수준 (Autonomy Level)

- [x] **적극(Thorough)** — 갈림길은 사용자가 확정한다.
- [ ] 보통(Balanced)
- [ ] 간략(Lean)

선택: **적극** · 선택일: 2026-11-11 · 변경 이력: 없음

> 사용자 규칙: 모든 작업은 설계·작업 계획 승인 후 실행한다. Claude는 커밋까지만 하고 push·병합·배포는 사용자가 별도로 요청한다.

## 1. 목적 / 배경

2026-11-11 Django 코드 검수에서 나온 결함 중, migration 없이 코드만으로 고칠 수 있고 지금 운영에서 피해가 나는 것을 먼저 막는다.
- 요청자마다 달라야 할 값(작성자 여부, 좋아요 상태)이 글 단위 Redis 캐시로 모든 방문자에게 공유되고, User 객체(비밀번호 해시 포함)가 Redis에 pickle된다.
- 댓글 삭제가 매번 롤백된다.
- 댓글 목록에 N+1이 있다.
- 쓰지 않는 개발 도구 import가 운영 import 실패 위험을 만든다.

캐시 구조 개선(키 체계, SCAN 제거, 무효화 시점, 공통 mixin 추출)은 **2단계(캐시 재설계)** 범위이며 이 그룹에서 하지 않는다.

## 2. 요구사항 레지스터

| Req-ID | 날짜 | 요청(원문 요약) | 도출된 요구사항 | 상태 | 연결 |
|---|---|---|---|---|---|
| REQ-001 | 2026-11-11 | "django 코드 검수, redis 캐시와 N+1 검토" → "작업 순서 정리, 반드시 설계·계획 후 실행" → "1단계 설계를 PR #9 병합 전에 미리 작성" | 검수 결과 1단계(C1·C2·N1·M2 + 형제 버그)를 고치는 설계와 작업 계획을 문서로 남긴다. 코드는 PR #9 병합 후 승인을 받아 작성한다. | Active | charter INV-1~5, ADR-001~005 |
| REQ-002 | 2026-11-11 | "1단계 설계 승인한다. PR은 사용하지 않는다. push는 차후 수동으로 요청하겠다. 커밋만 관리해줘." | ADR-001~005를 Accepted로 확정한다. GitHub PR을 쓰지 않는다. `docs/sentry-error-remediation-plan` 브랜치는 로컬 merge 커밋으로 main에 합치고(사용자 요청 시), 1단계는 그 main 위에서 구현한다. push는 사용자가 따로 요청한다. | Active | C-5, C-6, ADR-001~005 |
| REQ-003 | 2026-11-11 | "runserver로 테스트가 가능하다. nginx·gunicorn 등 인프라는 고려할 게 없다. Redis만 docker 단일 컨테이너. sqlite가 아닌 DB가 필요하면 WSL 컨테이너 사용" → "권장안대로" | 검증 환경은 `runserver`(`config.settings.dev`) + WSL docker 컨테이너 2개(`devspoon-redis` 26379, `devspoon-postgres` 25432, 새 named volume)로 한다. nginx 차단·서버 배포 절차는 계획에서 뺀다. Python 가상환경은 worktree의 `.venv`에 `poetry.lock` 기준으로 만든다. 다른 프로젝트 컨테이너와 DB 백업 경로는 건드리지 않는다. | Active | C-7, run-log §로컬 적용·검증 절차 |

## 3. 설계 결정 기록 (ADR)

| ADR-ID | 날짜 | 결정 | 근거 | 상태 | supersedes |
|---|---|---|---|---|---|
| ADR-001 | 2026-11-11 | `user_auth`는 `request.user`가 아니라 **요청자가 작성자인지 나타내는 bool**로 바꾸고, 캐시 분기 **밖에서** 요청마다 계산한다. `like_state`도 요청마다 계산한다. | 템플릿 9개가 `{% if user_auth %}`만 쓰므로 템플릿은 그대로 두고 값만 바꾸면 된다. `AnonymousUser`가 참으로 평가돼 버튼이 모두에게 보이던 문제도 함께 사라진다. | Accepted | — |
| ADR-002 | 2026-11-11 | 블로그 상세는 `pre_board`·`next_board`만 캐시하고, 캐시 존재 여부를 판단하는 기준 키를 `user_auth`에서 `pre_board`로 바꾼다. 요청자별 값은 캐시를 읽은 **뒤에** 덮어쓴다. | 배포 직후 Redis에 남아 있는 옛 `user_auth`·`like_state` 키를 읽더라도 요청자별 값이 덮어쓰므로 노출되지 않는다. | Accepted | — |
| ADR-003 | 2026-11-11 | board 상세 뷰의 `get_context_data` 캐시 블록은 제거한다. | 이 블록이 캐시하던 것은 `user_auth` 하나뿐이었다. 제거하면 남는 캐시가 없다. | Accepted | — |
| ADR-004 | 2026-11-11 | 댓글 목록은 `user_auth`를 빼고 캐시한다. 캐시에서 읽든 DB에서 읽든 응답 직전에 요청자 기준으로 `user_auth`를 붙인다. `post`/`board` 값은 `*_id`로 읽는다. | 캐시 재사용은 유지하면서 요청자별 값만 분리한다. `*_id`는 추가 쿼리가 없다. | Accepted | — |
| ADR-005 | 2026-11-11 | 댓글 `post_delete` 시그널은 삭제된 행을 다시 조회하지 않고 `instance.post_id`(board는 `board_id`)로 `filter(pk=..., reply_count__gt=0).update(reply_count=F(...) - 1)`을 실행한다. | 지금은 `Collector.delete`의 atomic 블록 안에서 `DoesNotExist`가 나서 삭제 전체가 롤백된다. 조건부 UPDATE 한 문장이면 race 없이 음수도 막는다. | Accepted | — |

> ADR은 사용자 승인 시 Accepted로 바꾼다.

## 4. 불가침 제약

- C-1: 요청자별 값(작성자 여부, 좋아요 상태, User 객체)은 공유 캐시에 저장하지 않는다. — REQ-001
- C-2: 서버 쪽 수정·삭제 권한 검사(`request.user != author` → `PermissionDenied`)는 그대로 유지한다. 이번 변경은 화면 표시만 바로잡는다. — REQ-001
- C-3: migration을 만들지 않는다. 모델 필드·DB 스키마는 바꾸지 않는다. — REQ-001
- C-4: 2단계 범위(키 체계, SCAN, 무효화 시점, mixin 추출)는 건드리지 않는다. — REQ-001
- C-5: 커밋까지만 하고 push·병합·배포는 하지 않는다. — 사용자 지시
- C-6: GitHub PR을 쓰지 않는다. 브랜치 통합은 사용자가 요청할 때 로컬 merge 커밋으로 한다. — REQ-002
- C-7: WSL의 기존 컨테이너(다른 프로젝트)와 로컬 DB 백업은 읽지도 바꾸지도 연결하지도 않는다. 검증용 컨테이너는 새 이름·새 포트·새 볼륨만 쓴다. — REQ-003

## 5. 변경 이력
- v0.1 (2026-11-11): 최초 작성. 설계만 하고 코드는 아직 작성하지 않음.
- v0.2 (2026-11-11): 사용자 설계 승인. ADR-001~005 Accepted. REQ-002(PR 미사용), C-6 추가.
- v0.3 (2026-11-11): REQ-003(runserver + WSL 컨테이너 검증, 인프라 제외), C-7 추가.

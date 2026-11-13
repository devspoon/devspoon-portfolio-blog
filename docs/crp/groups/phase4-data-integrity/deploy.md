# 4단계 운영 반영 절차 (phase4-data-integrity, ADR-005)

> 이 저장소는 migration 파일을 저장소에 두지 않고 서버에서 `makemigrations`로 만든다.
> 좋아요 unique 제약 migration은 **중복이 남아 있으면 실패**하므로, 아래 순서를 지킨다.
> 모든 명령은 운영 설정(`--settings=config.settings.prod` 등 서버에서 쓰는 설정)으로 실행한다.

## 순서

| # | 할 일 | 명령 | 확인할 것 |
|---|---|---|---|
| 1 | **DB 백업** | (서버의 기존 백업 방법) | 백업 파일이 만들어졌는지 |
| 2 | 코드 배포 | (기존 배포 방법) | 서버 재시작. 이 시점부터 새 좋아요 토글이 중복을 만들지 않는다 |
| 3 | 정리 대상 확인 | `python manage.py fix_data_integrity --dry-run` | 줄마다 `중복 좋아요 N건`, `like_count 바로잡기 N건`, `table_name 맞추기 N건`. 아무것도 바뀌지 않는다 |
| 4 | 정리 실행 | `python manage.py fix_data_integrity` | 3번과 같은 숫자 |
| 5 | 재실행(확인) | `python manage.py fix_data_integrity` | 모든 줄이 `0건` |
| 6 | migration 생성 | `python manage.py makemigrations blog` | `Create constraint unique_<모델>like_user_post on model <모델>like` 5개만 나와야 한다. 다른 변경이 나오면 멈추고 확인 |
| 7 | migration 적용 | `python manage.py migrate` | `Applying blog.000N_... OK` |

## 되돌리기

- 4번 이후 문제가 생기면: 1번 백업으로 복원한다. 정리 명령은 중복 좋아요 행을 **삭제**하므로 백업 없이는 되돌릴 수 없다.
- 7번만 되돌리려면: `python manage.py migrate blog <이전 migration 번호>`(제약만 제거, 데이터는 그대로).

## 이 단계가 바꾸는 것

- 좋아요: (사용자, 글)마다 가장 먼저 만든 행만 남는다. `like_count`는 실제 좋아요한 사용자 수가 된다(화면 숫자가 바뀔 수 있음).
- `table_name`: 모든 글이 모델 클래스 이름(`BlogPost`, `Notice` 등)이 된다. `updated_at`은 바뀌지 않는다.
- 사용자·글이 비어 있는 좋아요 행은 건드리지 않는다(제약 대상 아님).

## 리허설 기록 (2026-11-13, 로컬 dev DB — PostgreSQL 컨테이너 `devspoon-postgres`)

- 시작 상태: `blog.0003`(제약) 미적용, 글 23에 같은 사용자 좋아요 3행 + 다른 사용자 1행, `like_count` 1, 블로그 글 16개 `table_name` 빈 값
- 3번 dry-run: 중복 2건, `like_count` 1건, `table_name` 16건 — 데이터 변화 없음
- 4번: 같은 숫자로 실행 → 좋아요 2행(사용자 2명), `like_count` 2, `table_name` `BlogPost`
- 5번: 모든 줄 0건
- 6번: `AddConstraint` 5개만
- 7번: `Applying blog.0003_bloglike_unique_bloglike_user_post_and_more... OK`
- 이후 같은 (사용자, 글) 삽입 → `IntegrityError: duplicate key value violates unique constraint "unique_bloglike_user_post"`

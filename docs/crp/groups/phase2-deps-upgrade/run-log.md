# Run Log — phase2-deps-upgrade (라운드 로그 + 수렴 판정)

## 라운드 기록

### Round 0 — 2026-11-12 (base SHA: `584a955`, 브랜치 `crp/phase2-deps-upgrade`)
- **트리거:** 사용자 요청("모든 패키지 최신화 허용", U1~U3 권장안)
- **조사:** `poetry show --outdated --top-level` 28개. 임시 사본(`pyproject.toml`·`poetry.lock`)에서 해석 시험:
  - Python `^3.11`에서는 Django 6.x 해석 불가(6.x는 Python ≥3.12)
  - Django `^6.1`은 `django-celery-beat` 2.9.0(`Django <6.1`) 때문에 해석 불가
  - Django `^6.0` + 주요 메이저 전부 → 해석 성공(Django 6.0.10, allauth 65.22.0, recaptcha 4.1.0, django-redis 7.0.0, sentry-sdk 2.74.0, debug-toolbar 8.0.0, silk 5.6.0, celery 5.7.0, redis 8.1.0)
  - Django 5.0·6.0 릴리스 노트 대조: `DEFAULT_AUTO_FIELD`는 이미 BigAutoField, `USE_TZ=True`, 로그아웃은 자체 View라 해당 없음. 인자 없는 `format_html` 2곳 발견(F-001)
- **수렴 판정:** `NOT CONVERGED`(설계 단계)

## 작업 계획 (승인 후 실행 — 순서 고정)

각 하위 단계는 같은 절차를 따른다.
1. `pyproject.toml` 조건 변경 → `poetry lock` → `poetry install --with dev,test`
2. `manage.py check`(INV-2), 전체 pytest(INV-1), 우리 앱 `makemigrations --check --dry-run`(INV-3)
3. 서드파티 migration이 있으면 dev DB에 `migrate`
4. runserver 점검표(INV-4, charter §3)
5. 실패나 경고가 나오면 ledger에 기록. 수정이 C-3 범위 안이면 수정하고, 밖이면 멈추고 묻는다
6. 하위 단계별 커밋

| 순서 | 하위 단계 | 특이 사항 |
|---|---|---|
| 0 | 기준선 | 업그레이드 전 우리 앱 migration(이미 생성됨, git 무시)과 `makemigrations --check` 상태 확인 |
| 1 | 2-a 정리·저위험 | `testing.yml` Python 3.12 · `django-nose` 제거 · `isort` dev 그룹 |
| 2 | 2-b Django 5.2 LTS | 끝에서 `RemovedInDjango60Warning`을 오류로 바꿔 pytest(INV-5). F-001 수정 |
| 3 | 2-c Django 6.0.10 | — |
| 4 | 2-d 서드파티 메이저 | 묶음: ① django-redis 7(+redis-py) ② recaptcha 4(F-002) ③ allauth 65(F-003) ④ sentry 2·debug-toolbar 8·extensions 4·silk ⑤ imagekit 6·mptt 0.21·anymail 15·rangefilter 0.15·uvicorn. 묶음마다 2단계 검증 |
| 5 | 마무리 | `poetry show --outdated --top-level` 결과 기록, 수렴 판정 |

## 심각도 추세
| Round | CRIT | HIGH | MED | LOW | 신규 Fix | 판정 |
|---|---|---|---|---|---|---|
| 0 | 0 | 2 | 1 | 0 | 3 | NOT CONVERGED(설계) |

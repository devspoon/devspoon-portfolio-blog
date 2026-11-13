# Design Baseline — template-phase1-security (템플릿 고도화 1단계: 보안 긴급 수정 + 테스트 안전망)

> 이 그룹의 요구사항·설계 결정의 단일 기준. append-only — 항목은 지우지 않고 상태만 바꾼다.

## 0. 질의 수준 (Autonomy Level)
- [x] **적극(Thorough)**
- [ ] 보통(Balanced)
- [ ] 간략(Lean)

선택: **적극** · 선택일: 2026-11-11 · 변경 이력: 없음

## 1. 목적 / 배경
템플릿(HTML·CSS·JS) 전문가 수준 고도화(5단계 제안)의 1단계. 디자인 개편 전에 운영 중인 보안 결함
(저장형 XSS, GET 요청에 의한 상태 변경/CSRF)을 막고, 이후 단계의 회귀를 잡을 테스트 안전망을 만든다.

## 2. 요구사항 레지스터
| Req-ID | 날짜 | 요청(원문 요약) | 도출된 요구사항 | 상태 | 연결 |
|---|---|---|---|---|---|
| REQ-001 | 2026-11-11 | 템플릿 HTML 구조·CSS 통합·JS 개선 방안 제안, 디자인 스킬로 고도화 | 5단계 개선안 제안(코드 무변경) | Done | — |
| REQ-002 | 2026-11-11 | Bootstrap 유지, 빌드 없이, 1단계부터 시작 | 1단계: 보안 2종(XSS·GET 상태변경) + 형제 버그 전수 수정 + 렌더 테스트 안전망 | Active | ADR-001~005 |
| REQ-003 | 2026-11-11 | 모든 작업은 설계 및 작업 계획 후 실행 | 코드 편집 전 설계·계획 승인 STOP | Active | C-1 |

## 3. 설계 결정 기록 (ADR)
| ADR-ID | 날짜 | 결정 | 근거 | 상태 | supersedes |
|---|---|---|---|---|---|
| ADR-001 | 2026-11-11 | 상태 변경 뷰는 POST만 허용: 게시글 Delete 8 + 댓글 Delete 8 = `http_method_names = ["post"]`(get 오버라이드 제거), `UserDeleteView` = `LoginRequiredMixin` + `post`, 블로그 Like 5 = `get`→`post` | GET 상태 변경은 `<img src>` 한 줄로 CSRF 가능. 댓글 Delete는 `DeleteView`라 get 제거만 하면 확인 템플릿 부재로 500 → 메서드 제한이 정확 | Accepted | |
| ADR-002 | 2026-11-11 | 댓글 렌더링: `blog_apis.js`에 `escapeHtml()` 추가, 문자열 필드(author·comment·created_at·thumbnail)에 적용. JSON API 계약은 그대로 | 최소 diff로 `insertAdjacentHTML` XSS 차단. `<template>` 전환은 4단계(JS 개선)에서 | Accepted | |
| ADR-003 | 2026-11-11 | 본문 HTML: `nh3` 의존성 추가, 기존 `public_tags`에 `sanitize_html` 필터 추가, 상세 템플릿 8곳의 `content\|safe` 교체. 허용 목록 = Summernote 출력 태그 + `style`(안전 속성만). 홈 `item.title\|safe` 4곳은 `\|safe` 제거 | 렌더 시점 정제라 기존 DB 데이터도 보호. nh3는 bleach 후속(Rust, 유지보수 중) | Accepted | |
| ADR-004 | 2026-11-11 | 블로그 5종·공지 Create 뷰는 staff만 허용(일반 회원 403). 방명록·재활성화는 현행 | 사용자 확정. 쓰기 버튼만 숨기던 것을 서버에서 강제 | Accepted | |
| ADR-006 | 2026-11-11 | 의존성 관리는 poetry(pipx 설치)로: `poetry add nh3`로 pyproject·lock 동시 갱신, `requirements/dev.txt`에도 반영. 테스트는 poetry venv에서 실행 | 사용자 지시(lock 정합성 유지) | Accepted | |
| ADR-007 | 2026-11-11 | 테스트는 WSL(Linux) venv + WSL redis-server에서 실행. Windows poetry venv는 lock 갱신용 | nh3 DLL이 Windows 앱 제어 정책에 차단됨. 운영·CI와 같은 Linux 환경(사용자 확정) | Accepted | ADR-006 일부 |
| ADR-008 | 2026-11-11 | staff 검사는 braces 대신 Django `UserPassesTestMixin` 기반 `common/mixin/views.py` StaffRequiredMixin | braces StaffuserRequiredMixin은 Django LoginRequiredMixin과 `handle_no_permission` 충돌, `raise_exception`이 비로그인 리다이렉트까지 403으로 바꿈 | Accepted | |
| ADR-005 | 2026-11-11 | 삭제 UI: 상세 8곳의 수정/삭제 링크를 `{% url %}`로 생성, 삭제는 `<form method="post">{% csrf_token %}`. `blog.js`의 수정/삭제 URL 재작성 블록 제거. 댓글 삭제 = `axios.post` 후 새로고침. 회원 탈퇴 버튼 = POST 폼 | JS URL 조작 의존 제거, CSRF 토큰 동반 | Accepted | |

## 4. 불가침 제약
- C-1: 코드 편집 전 설계·작업 계획 승인 (REQ-003)
- C-2: 기존 화면 동작(작성·수정·댓글·좋아요·페이지네이션) 회귀 금지 — 렌더/기능 테스트로 확인
- C-3: 댓글 JSON API 응답 형식 불변 (ADR-002)
- C-4: Summernote 기본 서식(굵게·색상·목록·표·이미지·링크·코드)은 정제 후에도 표시 (ADR-003)

## 5. 변경 이력
- v0.1 (2026-11-11): 최초 작성 — 조사 결과와 1단계 설계.

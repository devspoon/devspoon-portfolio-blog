# Residual Risk — <그룹 이름> (잔여 위험 등록부)

> **재기 금지 목록.** 여기 "수용(Accepted)"으로 박제된 항목은 *의도적으로 고치지 않기로* 결정된
> 것이다. 다음 라운드에서 이걸 새 finding 으로 다시 올리면 안 된다(증상 확대의 원천). 고쳐야 하면
> 그것은 "새 결함"이 아니라 **계약 변경 제안** — charter 를 먼저 바꾼다.

| ID | 항목 | Severity | 왜 비범위인가(계약 근거) | 수용일 | 재평가 조건 |
|---|---|---|---|---|---|
| R-001 | 홈 `latest`가 `order_by("created_at")` 오름차순 → 가장 오래된 9건 선택, `.values("author")`는 pk | MED | 뷰 로직(디자인 범위 밖). 템플릿은 `dictsortreversed`로 표시 순서만 보정, 작성자는 홈에 표시 안 함 | 2026-11-12 | STOP ②에서 수정 승인 시 |
| R-002 | 상세 댓글 UI(레거시 JS 문자열 조립): Save 버튼 대비 4.22, `javascript:` 페이지 링크(SEO crawlable-anchors) | LOW | 5단계 JS 재작성 범위(comments.html + `<template>`) | 2026-11-12 | 5단계 완료 시 재측정 |
| R-003 | 본문(사용자 작성 Summernote HTML) 이미지에 alt 없음 → Lighthouse image-alt | LOW | 콘텐츠 문제. sanitizer 변경은 계획 밖 | 2026-11-12 | sanitize 시 `alt=""` 기본값 추가를 승인하면 |
| R-004 | 새 UI 문자열(영어 msgid)이 .po 미번역 → 한국어 화면에 영어 노출 | MED | 문자열이 4b까지 계속 바뀜 | 2026-11-12 | 7단계에서 makemessages + 번역 |
| R-005 | 레거시 CSS가 남은 페이지(상세 포함)에서 헤더 검색창 패딩 등 누수 | LOW | 6단계 legacy.css 삭제로 해소 | 2026-11-12 | 4b·6단계 |
| R-006 | 좋아요 버튼 `aria-pressed` 없음(레거시 JS가 `.clicked`만 토글) | LOW | 5단계 like.js에서 상태 동기화 | 2026-11-12 | 5단계 |

<!--
예: "입력 X 가 비표준 형식이면 깨질 수 있음" → 계약 2-4 비목표라 Accepted.
    재평가 조건: '입력 X 비표준 형식 지원'이 charter 계약에 추가되면.
-->

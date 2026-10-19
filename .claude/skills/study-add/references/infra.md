# 인프라 상세 (sidebar · knowledge-graph · README)

navbar, client.js, studies.js, 컴포넌트는 새 스터디를 자동으로 인식하므로 손대지 않는다. 고칠 곳은 아래 세 군데다.

## 1. config.mjs sidebar

`docs/.vuepress/config.mjs`의 `sidebar` 객체 마지막 스터디 블록 뒤에 추가한다. 소스 디렉토리는 `docs/_study/`(언더스코어)지만 URL과 sidebar 키는 `/study/`(언더스코어 없음)다 — 섞으면 `missing sidebar config` 경고가 난다.

```js
'/study/{slug}/': [
  {
    text: '섹션 이름',
    collapsible: false,
    children: [
      { text: '소개', link: '/study/{slug}/' },
      { text: 'CH1. 챕터 제목', link: '/study/{slug}/01-xxx' },
    ],
  },
  // … 섹션 반복
  {
    text: '부록',
    collapsible: false,
    children: [
      { text: '용어집', link: '/study/{slug}/appendix-glossary' },
      { text: '참고 자료', link: '/study/{slug}/appendix-references' },
    ],
  },
],
```

검증: `node --check docs/.vuepress/config.mjs`

## 2. knowledge-graph.js

`docs/.vuepress/data/knowledge-graph.js`의 `nodes`·`edges`에 추가한다.

```js
{ id: '{slug}', label: '표시명\n(부가)', size: 26, status: 'active', link: '/study/{slug}/', x: 0.00, y: 0.00 },
{ source: '{부모 id}', target: '{slug}' },
```

- size: 대분류 36, 스터디 26, 하위 20~24
- status: `'active'`(링크 있음) / `'planned'`(점선 원). 이미 `planned`로 있는 노드가 이 스터디라면 새로 만들지 말고 그 노드를 `active`로 바꾸고 link를 단다.
- 대분류: `smart-agriculture`(좌측), `software`(우측), `ai`(중앙 하단). 부모로 쓸 만한 기존 노드(`network`, `aws`, `backend`, `infra`, `auth` 등)는 파일을 열어 확인한다.
- 좌표: 노드 원과 라벨이 겹치지 않도록 기존 노드와 거리 0.06 이상. 손으로 계산하지 말고 스크립트를 쓴다.
  ```bash
  python3 .claude/skills/study-add/scripts/kg_spot.py 0.79 0.47 --suggest
  ```

검증: `node --check docs/.vuepress/data/knowledge-graph.js`

## 3. README.md (소개 페이지)

`docs/_study/{slug}/README.md`. frontmatter의 title·description·tags가 스터디 카드(StudyCard)와 목록에 그대로 쓰인다.

```yaml
---
title: "스터디 제목"
description: "한두 문장 — 무엇을 어디까지 다루는지"
date: YYYY-MM-DD
tags: [태그1, 태그2, …]
---
```

본문 구성(골든 샘플: `docs/_study/webrtc/README.md`):
1. `# 제목` + 도입 문단(무엇이고, 어떤 관점으로, 누구를 위해)
2. "이 스터디에서 배우는 것" — 섹션별 불릿
3. "전체 구조" — 주제의 핵심 구성요소 개관 다이어그램(`readme-overview`)
4. "학습 로드맵" — 섹션 단계 체인 다이어그램(`readme-roadmap`, `docs/_study/webrtc/_diagrams/readme-roadmap.py`를 섹션 수에 맞게 고쳐 쓴다)
5. "전체 목차" — 섹션별 표 `| 챕터 | 제목 | 한줄 설명 |`, 링크 `/study/{slug}/{파일명}`
6. "관련 글" — 블로그 포스트·다른 스터디 링크

## 흔한 빌드 에러

마크다운 원인 에러(`<br/>`, 본문 `{{`, `<태그>` 텍스트 등)는 `references/chapter-format.md`의 "마크다운 함정" 표를 본다. 인프라 쪽 에러는 다음과 같다.

| 에러 | 원인 | 해결 |
|------|------|------|
| `missing sidebar config` (해당 스터디 페이지) | sidebar 키가 `/_study/` 이거나 경로 오타 | `/study/{slug}/` |
| `localStorage.getItem is not a function` | @vue/devtools-kit SSR 버그 | `ssr-polyfill.cjs`로 해결됨(조치 불필요) |

기존 포스트들의 `missing sidebar config` 경고는 원래 있던 것이라 무시한다. 새 스터디 관련 경고만 본다: `grep -i "{slug}" <build.log>`.

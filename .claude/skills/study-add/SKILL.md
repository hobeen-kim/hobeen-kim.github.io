---
name: add-study
description: 블로그에 새로운 스터디(공부하기) 콘텐츠를 추가하는 워크플로우. 챕터 구조 설계, 인프라 설정, 콘텐츠 생성을 포함.
triggers:
  - "스터디 추가"
  - "공부하기 추가"
  - "새 스터디"
  - "add study"
---

# 블로그 스터디 추가 스킬

VuePress 블로그에 새로운 스터디(공부하기) 섹션 콘텐츠를 추가하는 워크플로우.

## 전제 조건

- 프로젝트 루트: `/Users/hobeen/private/hobeen-kim.github.io`
- 기존 공부하기 인프라가 이미 구축되어 있음 (StudyList, StudyCard, config sidebar, studies.js)
- 새 스터디는 `docs/_study/{slug}/` 디렉토리에 추가

## 워크플로우

### 1단계: 스터디 설계 (브레인스토밍)

사용자에게 다음을 확인:
- **주제**: 무엇에 대한 스터디인가
- **대상**: 비개발자 포함? 팀 내부? 외부 공개?
- **깊이**: 기초부터? 특정 레벨부터?

확인 후 챕터 목차를 작성:
- 학습 순서가 논리적인 bottom-up 구조
- 각 챕터에 4~7개 절
- 관련 챕터끼리 섹션으로 그룹핑

목차를 critic 에이전트로 리뷰받고, 타당한 피드백만 반영.

### 2단계: 인프라 추가

#### 2-1. 디렉토리 생성
```bash
mkdir -p docs/_study/{slug}
mkdir -p docs/.vuepress/public/images/{slug}
```

#### 2-2. config.mjs sidebar 추가

`docs/.vuepress/config.mjs`의 `sidebar` 객체에 새 경로 추가:
```js
sidebar: {
  // 기존 스터디 사이드바...
  '/study/{slug}/': [
    {
      text: '섹션 이름',
      children: [
        '/study/{slug}/',
        '/study/{slug}/01-chapter-name',
        // ...
      ],
    },
    // 추가 섹션...
  ],
}
```

**주의:** 
- 소스 디렉토리는 `docs/_study/` (언더스코어)
- URL/sidebar 경로는 `/study/` (언더스코어 없음) — VuePress가 자동 변환

#### 2-3. 스터디 README.md (소개 페이지)

`docs/_study/{slug}/README.md` 생성:
```yaml
---
title: "스터디 제목"
description: "한줄 설명"
date: YYYY-MM-DD
tags: [태그1, 태그2]
---
```
- Mermaid flowchart로 학습 로드맵 포함
- 전체 목차 (챕터별 링크)

### 3단계: 콘텐츠 작성

각 챕터 마크다운 파일을 생성. 파일명: `{번호}-{영문이름}.md`

#### 페이지 구조 패턴
```markdown
---
title: "챕터 제목"
description: "한줄 설명"
date: YYYY-MM-DD
tags: [관련태그]
---

# 챕터 제목

## 학습 목표
- 목표1
- 목표2

## 절1 제목
설명 + Mermaid 다이어그램 + 코드 예제

## 절2 제목
...

::: tip 핵심 정리
요약 내용
:::

## 다음 챕터
[다음 챕터 제목](다음경로)으로 이어집니다.
```

#### 문체 규칙
- **반말 평서체(해라체)** 사용 — `~이다`, `~한다`, `~있다`, `~된다` 등. `~입니다`, `~합니다`, `~있습니다` 등 경어체 금지

#### 시각화 도구 활용
- VuePress 마크다운 컨테이너:
  - `:::tip 제목` — 핵심 정리, 팁
  - `:::info 제목` — 참고 정보, 부연 설명
  - `:::warning 제목` — 주의사항, 안전 관련 경고
  - `:::details 제목` — 접기/펼치기 (긴 코드 예제, 심화 내용)
  - `:::tabs` + `@tab` — 멀티 언어 코드 예제 (C/Python 등)
- GitHub 스타일 callout(`> [!TIP]`, `> [!INFO]`) 사용 금지 — VuePress에서 렌더링되지 않음

#### Mermaid 다이어그램 규칙
- 각 챕터에 최소 2개 이상의 Mermaid 다이어그램 포함
- 활용 가능한 유형: flowchart, sequenceDiagram, packet-beta, stateDiagram-v2, timeline(`<br>` 미지원, 쉼표로 구분), xychart-beta, pie, mindmap, gantt, quadrantChart(한글/특수문자 라벨 미지원, 영문만 사용)
- `stateDiagram-v2`에서 줄바꿈은 `\n` 대신 `<br>` 사용
- `<br/>` 사용 금지 — Vue 컴파일 에러 발생. `<br>` 사용
- `**bold**한글` 패턴 금지 — CommonMark에서 닫는 `**` 뒤에 한글이 바로 오면 bold가 적용되지 않음. `<strong>bold</strong>한글` 사용

#### 콘텐츠 병렬 작성
- 관련 챕터 2~3개씩 그룹으로 묶어 executor 에이전트에 위임
- 그룹 간 의존성이 없으므로 모두 병렬 실행 가능
- 각 에이전트에 해당 챕터의 절 구성과 기술 상세를 프롬프트로 전달

### 4단계: 빌드 검증

```bash
cd /Users/hobeen/private/hobeen-kim.github.io
npm run docs:build
```

#### 흔한 빌드 에러와 해결

| 에러 | 원인 | 해결 |
|------|------|------|
| `Illegal '/' in tags` | Mermaid 내 `<br/>` | `<br>`로 교체 |
| `Attribute name cannot contain "` | Mermaid 내 특수문자 | `escapeHtml` 처리됨 (현재 config에 적용) |
| `localStorage.getItem is not a function` | @vue/devtools-kit SSR 버그 | `ssr-polyfill.cjs`로 해결됨 |
| `missing sidebar config` | sidebar 경로 불일치 | `/study/` (언더스코어 없음) 사용 확인 |

### 5단계: 배포

```bash
git add docs/_study/{slug}/ docs/.vuepress/config.mjs
git commit -m "feat: {스터디 이름} 스터디 추가"
git push origin master
```

GitHub Actions가 자동 배포.

## 기존 인프라 파일 참조

| 파일 | 역할 |
|------|------|
| `docs/.vuepress/config.mjs` | navbar, sidebar, define, Mermaid markdown-it 플러그인 |
| `docs/.vuepress/client.js` | StudyList 등록, Mermaid CDN 로드 (router.afterEach) |
| `docs/.vuepress/utils/studies.js` | `_study/` 서브디렉토리 스캔, frontmatter 파싱 |
| `docs/.vuepress/components/StudyCard.vue` | 스터디 카드 (썸네일 + 제목/설명/태그) |
| `docs/.vuepress/components/StudyList.vue` | 스터디 목록 (`__STUDIES__` 전역변수) |
| `docs/.vuepress/components/home/RecentStudies.vue` | 홈페이지 공부하기 섹션 |
| `docs/.vuepress/components/home/Home.vue` | 홈페이지 (RecentStudies 포함) |
| `docs/.vuepress/ssr-polyfill.cjs` | localStorage SSR 폴리필 |
| `docs/_study/README.md` | 공부하기 목록 페이지 (`<StudyList/>`) |

## 새 스터디 추가 시 수정 필요한 파일

1. `docs/.vuepress/config.mjs` — sidebar에 새 경로 추가 (이것만 수정)
2. `docs/_study/{slug}/` — 새 디렉토리에 README.md + 챕터 파일들 생성

navbar, client.js, studies.js, 컴포넌트는 수정 불필요 — 자동으로 새 스터디를 인식함.

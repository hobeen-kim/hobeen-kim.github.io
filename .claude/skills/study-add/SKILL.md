---
name: study-add
description: hobeen-kim.github.io VuePress 블로그에 여러 챕터짜리 새 스터디(공부하기) 시리즈를 추가하는 엔드투엔드 워크플로우 — 목차 설계와 critic 리뷰, 사실 조사, 공용 집필 가이드, 서브에이전트 병렬 집필, matplotlib 라이트/다크 다이어그램, 린트·일관성 검증·독자 테스트, 부록, 빌드·커밋·배포 확인까지. 사용자가 "스터디 추가", "새 스터디", "공부하기 추가", "OO 스터디 만들어줘", "OO 공부해서 블로그에 정리해줘", "OO 학습 시리즈", "/study-add OO"처럼 하나의 주제를 여러 챕터로 체계적으로 정리해 블로그에 올리려 할 때는 반드시 이 스킬을 쓴다. 기존 스터디 챕터에 내용을 보충하는 일은 study-supplement, 단일 기술 글은 post-create, 짧은 기록은 log-create가 맡는다.
triggers:
  - "스터디 추가"
  - "공부하기 추가"
  - "새 스터디"
  - "add study"
---

# 블로그 스터디 추가 스킬

`docs/_study/{slug}/`에 소개 페이지 + 챕터 N개 + 부록을 만들고, 다이어그램·sidebar·knowledge-graph를 붙여 배포까지 끝낸다. 한 번에 수십 개 챕터를 서브에이전트로 병렬 집필하므로, 이 스킬의 대부분은 "병렬로 쓰되 하나의 책처럼 정확하고 일관되게" 만드는 장치다.

## 왜 이렇게 진행하나

- **정확성이 생명이다.** 스터디는 오래 참조된다. 낡은 한도·가격·API 하나가 전체 신뢰를 깎는다. 그래서 빠르게 변하는 사실은 집필 전에 공식 출처로 조사해 사실 파일로 고정하고, 확인 못 한 것은 본문에 "확인 필요"로 남긴다.
- **병렬 집필은 일관성을 깬다.** 에이전트는 자기 챕터만 본다. WebRTC 스터디에서는 재연결 주기가 장마다 40/50/55분으로, 녹화 권고가 장마다 다르게 나왔다. 공용 집필 가이드(용어 표기·공유 결정)로 예방하고, 집필 후 일관성 검증 에이전트로 잡는다.
- **기계로 잡을 수 있는 건 기계로 잡는다.** 손으로 grep하면 놓친다(실제로 체크박스 8줄을 놓쳤다). `scripts/lint_study.py`가 금지 패턴·링크·이미지·prev/next·sidebar 등록을 한 번에 본다.
- **사용자 시간을 아낀다.** 합리적 기본값이 있으면 묻지 않고 정한 뒤 한 줄로 알린다. 진행 보고는 짧게.

## 완료 정의

- `lint_study.py {slug}`(`--pending` 없이) ERROR 0, WARN은 의도한 것만
- `npm run docs:build` 성공, 빌드 로그에 `{slug}` 관련 경고 없음
- 챕터가 `references/chapter-format.md` 체크리스트(학습 목표·절 수·다이어그램·확인 문제 분량 포함)를 지킨다
- 캡스톤(또는 종합) 챕터, 부록(용어집·참고 자료)
- sidebar·knowledge-graph 등록, README 로드맵
- 커밋·푸시 후 GitHub Actions 배포 성공 확인
- 최종 보고에 "확인 못 한 사실" 목록

## 0단계: 맥락 파악

1. 현재 스터디 목록: `ls docs/_study/` — 중복·연관 스터디를 확인한다. 목록을 이 스킬에 적어 두지 않는 이유는 금방 낡기 때문이다.
2. 교차 링크 후보: `grep -rli "<키워드>" docs/_posts docs/_study | head` — 관련 포스트 URL은 `/posts/{카테고리}/{파일명}`.
3. 사용자 맥락: 전역 CLAUDE.md·메모리의 직무·관심사로 독자와 예시 시나리오를 정한다(예: 디바이스 백엔드 → 농기계·로봇 시나리오).

## 1단계: 범위와 목차 설계

**범위는 추론부터.** 인자·대화·사용자 맥락으로 주제·대상·깊이의 기본값을 정한다. 주제 자체가 모호해 방향이 갈리는 경우(예: "클라우드"처럼 범위가 정해지지 않은 요청)만 묻는다. 정한 기본값은 한 줄로 알린다. slug는 영문 kebab-case.

**목차 설계 원칙:**
- bottom-up: 어떤 개념도 정의되기 전에 쓰이지 않게 한다. 의존이 역전된 챕터는 순서를 바꾸거나 개념을 앞 챕터로 옮긴다.
- 챕터당 4~7절, 관련 챕터 3~7개를 섹션으로 묶는다.
- 흐름: 원리 → 프로토콜/내부 구조 → 아키텍처·운영 → (해당되면) 제품·서비스 → 캡스톤 → 부록.
- 캡스톤: 스터디 전체를 하나의 실전 설계로 엮는 마지막 챕터. 흩어진 지식을 한 그림으로 묶는 자리라 학습 효과가 크다.
- 규모는 주제 폭에 맞춘다(보통 10~45챕터). 챕터마다 학습 목표 2~4개를 미리 적어 보면 너무 큰 챕터가 드러난다.

목차 초안을 scratchpad `{slug}-toc.md`에 쓰고 critic 에이전트로 리뷰받는다(`references/agent-prompts.md` A). 타당한 피드백만 반영하고, 반영한 것을 한두 줄로 사용자에게 알린다.

**사실 조사 병행:** 클라우드 서비스 한도·가격, 표준 상태, 라이브러리 버전, 서비스 종료 공지처럼 모델 기억이 낡았을 수 있는 사실이 핵심이면, critic 리뷰와 같은 턴에 사실 조사 에이전트를 띄운다(템플릿 B). 결과 `{slug}-facts.md`가 집필의 1차 근거가 된다.

## 2단계: 인프라와 집필 가이드

1. 디렉토리·헬퍼: `bash .claude/skills/study-add/scripts/setup_study.sh {slug}`
2. 공용 집필 가이드: `references/writing-guide-template.md`를 scratchpad `{slug}-writing-guide.md`로 채운다. 확정 목차, 절별 필수 내용, 용어 표기, 공유 결정이 들어간다. 이 파일이 모든 에이전트의 단일 규칙 원천이다.
3. 인프라 에이전트 1개(템플릿 C): sidebar, knowledge-graph, README + 로드맵. 상세는 `references/infra.md`. 본문 집필과 병렬로 돌린다.

## 3단계: 병렬 집필

- **묶음:** 관련 챕터 2~3개씩 에이전트 하나(템플릿 D). 사실 파일에 의존하지 않는 챕터부터 첫 웨이브로 띄우고, 의존하는 챕터(서비스·가격 등)는 사실 조사가 끝나면 두 번째 웨이브로 띄운다. 캡스톤도 다른 챕터를 링크만 하고 설계 결정에 집중하면 같은 웨이브에 넣을 수 있다.
- **파일 소유 경계:** 각 에이전트는 담당 챕터 .md와 자기 챕터 번호 접두사 다이어그램만 만든다. 커밋·빌드는 오케스트레이터만 한다. 동시에 같은 파일을 만지면 덮어쓰기 사고가 난다. 프롬프트에는 규칙을 반복하지 않고 가이드 경로만 준다(템플릿 D).
- **모델:** 집필은 상위 모델(opus), 인프라·부록 같은 기계적 작업은 sonnet.
- **진행 보고:** 완료 알림마다 한두 줄(완료 챕터, 다이어그램 수, 특이사항). 각 에이전트가 보고한 "확인 못 한 사실"은 모아 둔다 — 4단계 검증과 최종 보고에 쓴다.
- **기다리기:** 서브에이전트 완료 알림이 다시 깨워 주므로 폴링하지 않는다. 안전망 예약 깨우기(wakeup·cron 등)를 걸었다면 작업이 끝나는 즉시 해제한다. 남겨 두면 끝난 작업을 확인하는 턴이 계속 반복된다.

## 4단계: 검증

모든 챕터가 끝나면 순서대로:

1. **기계 린트:** `python3 .claude/skills/study-add/scripts/lint_study.py {slug} --pending` → ERROR 0까지 고친다. 부록이 아직 없으므로 `--pending`이 부록을 가리키는 링크를 WARN으로 낮춰 준다. WARN은 하나씩 의도 여부를 본다.
2. **1차 빌드(백그라운드 가능):** `npm run docs:build > {scratchpad}/build.log 2>&1` — 빌드 에러를 일찍 잡는다. 약 30초.
3. **검증 웨이브:** 아래 세 에이전트를 같은 턴에 띄우되, 챕터를 고치는 일은 한 번에 하나만 한다.
   - 일관성·사실 검증(템플릿 E, 챕터 수정): 챕터 간 수치·권고·용어 불일치, 사실 파일 대조, 비용 산술 검산. 집필 에이전트들이 남긴 의심 항목 중 중요한 것을 프롬프트에 넣는다.
   - 독자 테스트(템플릿 F, 읽기 전용): 집필 맥락 없는 에이전트가 샘플 챕터(첫 챕터, 가장 어려운 2~3개, 캡스톤)만 읽고 정의 전 용어·논리 비약·모호함을 보고한다. 지적 사항은 E가 끝난 뒤 executor에게 넘겨 고친다 — E와 동시에 같은 챕터를 고치면 덮어쓰기 사고가 난다.
   - 부록(템플릿 G, 부록 파일만): 용어집, 참고 자료. 본문 링크가 적으면 참고 자료가 빈약해지므로 표준·공식 문서·저장소의 정전 URL을 curl로 확인해 보강한다.
4. **마무리 확인:** `lint_study.py {slug}`(`--pending` 없이) → 재빌드 → 대표 다이어그램 2장(README 로드맵, 가장 복잡한 아키텍처 그림)을 직접 열어 본다.

## 5단계: 배포

```bash
git add docs/_study/{slug} docs/.vuepress/public/images/study-{slug} \
        docs/.vuepress/config.mjs docs/.vuepress/data/knowledge-graph.js \
        docs/.vuepress/public/sitemap.xml
git commit -F - <<'EOF'
feat: {스터디 이름} 스터디 추가

{한 문단 요약}

- {섹션별 구성 요약 3~6줄}
- matplotlib 다이어그램 N종(light/dark), sidebar·knowledge-graph 노드 추가

{세션 attribution 줄}
EOF
git push origin master
gh run list --limit 2   # "Deploy to GitHub Pages" success 확인 (1~2분)
```

`sitemap.xml`은 빌드가 갱신한다. 기존 커밋들도 함께 커밋해 왔으므로 포함한다. 이 스킬 호출 자체가 배포까지의 위임이므로 push 전에 다시 묻지 않는다.

## 6단계: 최종 보고

- 구성 표: 섹션 / 챕터 범위 / 내용
- 묻지 않고 정한 기본값과 판단(범위, critic 반영, 권고 결론 등)
- 검증 결과: lint, build, 배포
- 확인 못 한 사실 목록 — 사용자가 실무에 쓰기 전에 직접 확인할 것

## 중단 후 재개

챕터 파일은 디스크에 있으므로 `ls docs/_study/{slug}/`와 `lint_study.py`로 진행 상태를 복원한다. scratchpad의 가이드·사실 파일이 사라졌다면, 이미 쓴 챕터와 이 스킬의 템플릿으로 가이드를 다시 만들고 남은 챕터만 이어서 집필한다.

## 참고 파일

| 파일 | 언제 읽나 |
|------|-----------|
| `references/chapter-format.md` | 챕터 템플릿·체크리스트·마크다운 함정. 가이드 작성 시, 집필 에이전트가 읽는다 |
| `references/diagrams.md` | 다이어그램 스타일·경로·글꼴 함정·시각 검증 |
| `references/writing-guide-template.md` | 2단계 공용 집필 가이드를 만들 때 |
| `references/agent-prompts.md` | 단계별 서브에이전트 프롬프트(A 목차 리뷰 ~ G 부록) |
| `references/infra.md` | sidebar·knowledge-graph·README 형식, 흔한 빌드 에러 |
| `scripts/setup_study.sh {slug}` | 디렉토리 생성 + `_common.py` 복사 |
| `scripts/lint_study.py {slug} [--pending]` | 기계 점검(ERROR 시 exit 1). 집필 도중엔 `--pending` |
| `scripts/kg_spot.py X Y [--suggest]` | knowledge-graph 좌표 겹침 점검·빈자리 추천 |

## 기존 인프라 (수정 불필요, 문제 생길 때만 참고)

| 파일 | 역할 |
|------|------|
| `docs/.vuepress/utils/studies.js` | `_study/` 하위 디렉토리 스캔, README frontmatter 파싱 → 스터디 카드 |
| `docs/.vuepress/components/StudyList.vue`, `StudyCard.vue` | 공부하기 목록·카드 |
| `docs/.vuepress/components/home/RecentStudies.vue` | 홈 화면 최근 스터디 |
| `docs/.vuepress/styles/index.scss` | `-light/-dark.png` 테마 전환 규칙 |
| `docs/.vuepress/ssr-polyfill.cjs` | localStorage SSR 폴리필 |

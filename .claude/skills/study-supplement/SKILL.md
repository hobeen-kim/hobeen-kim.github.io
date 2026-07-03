---
name: study-supplement
description: 스터디 콘텐츠에 대해 질문에 답하고, 사용자 승인 시 해당 내용을 마크다운에 추가한 뒤 배포하는 워크플로우.
triggers:
  - "내용 보충"
  - "내용 추가"
  - "이거 설명해"
  - "이게 뭐야"
  - "supplement"
---

# 스터디 내용 보충 스킬

사용자가 스터디 관련 질문을 하면 답변하고, 해당 내용을 기존 챕터에 추가할지 확인 후 반영 및 배포.

## 전제 조건

- 프로젝트 루트: `/Users/hobeen/private/hobeen-kim.github.io`
- 스터디 콘텐츠 디렉토리: `docs/_study/{slug}/`
- 기존 챕터 파일이 존재해야 함

## 워크플로우

### 1단계: 질문 파악 및 답변

사용자의 질문을 분석:
- 어떤 스터디의 어떤 챕터에 해당하는 내용인지 판단
- 해당 챕터 파일을 읽어 현재 내용 확인
- 질문에 대해 상세하고 정확하게 답변

### 2단계: 내용 추가 제안

답변 후 반드시 되물음:

```
이 내용을 [챕터명]에 추가할까요?
```

사용자의 응답에 따라 분기:
- **"응"/"추가해"/"넣어"** → 3단계로 진행
- **"아니"/"괜찮아"** → 종료
- **"다른 챕터에"/"새 절로"** → 사용자가 지정한 위치에 추가

### 3단계: 내용 삽입

대상 챕터 파일을 수정:
- 기존 절의 내용을 보강하거나, 새 절(##)을 추가
- 기존 콘텐츠 패턴을 따름:
  - 교차 링크: 관련 블로그 포스트(`/posts/...`)나 다른 스터디 챕터(`/study/...`)가 있으면 본문에 링크 삽입
  - 문체: **반말 평서체(해라체)** 사용 — `~이다`, `~한다`, `~있다`, `~된다` 등. `~입니다`, `~합니다`, `~있습니다` 등 경어체 금지
  - 다이어그램이 적절한 경우 **matplotlib → PNG 방식**으로 포함 (아래 "다이어그램 작성 규칙" 참고). **Mermaid는 새 다이어그램에 사용하지 않는다** (기존 챕터에 이미 있는 mermaid는 그대로 둠)
  - 코드 예제가 필요한 경우 포함
  - `<br/>` 사용 금지 — `<br>` 사용
  - `**bold**한글` 패턴 금지 — CommonMark에서 닫는 `**` 뒤에 한글이 바로 오면 bold가 적용되지 않음. `<strong>bold</strong>한글` 사용
  - GitHub 스타일 callout(`> [!TIP]`, `> [!INFO]`) 사용 금지 — VuePress에서 렌더링되지 않음
- VuePress 마크다운 컨테이너 활용:
  - `:::tip 제목` — 핵심 정리, 팁
  - `:::info 제목` — 참고 정보, 부연 설명
  - `:::warning 제목` — 주의사항, 안전 관련 경고
  - `:::details 제목` — 접기/펼치기 (긴 코드 예제, 심화 내용)
  - `:::tabs` + `@tab` — 멀티 언어 코드 예제 (C/Python 등)
- 기존 내용을 삭제하거나 변경하지 않음 — 추가만

### 다이어그램 작성 규칙 (matplotlib → 라이트/다크 PNG 2벌)

새 다이어그램은 Mermaid가 아니라 **matplotlib으로 그려 PNG로 저장**하고 마크다운에서 이미지로 참조한다.

**스타일 원칙 — 가벼운 보조 그림:**
- 그림에는 **구조만** 담는다: 노드 이름(+ 괄호 1줄 부가), 그룹 라벨, 화살표+짧은 라벨. 설명은 본문의 몫이다.
- **금지**: 대제목·부제·하단 요약 문장·본문과 중복되는 박스 안 설명 서브텍스트 (절 제목과 본문이 그 역할을 한다)
- 범례는 색이 실제 정보를 구분할 때만 최소로
- figsize는 내용에 맞춰 작게 (기본 12×6, 복잡하면 14×8 정도까지)

**라이트/다크 2벌 필수:**
- 모든 다이어그램은 `{이름}-light.png` / `{이름}-dark.png` 두 장을 생성한다
- `docs/_study/{slug}/_diagrams/_common.py`의 `diagram()` 헬퍼가 두 팔레트로 자동 렌더링한다 (observability의 `_common.py`를 다른 스터디에 복사해 사용)
- 마크다운에는 두 장을 **연속 두 줄**로 참조한다 (같은 alt 텍스트):
  ```md
  ![다이어그램 설명](/images/study-{slug}/{이름}-light.png)
  ![다이어그램 설명](/images/study-{slug}/{이름}-dark.png)
  ```
- 테마 전환은 `docs/.vuepress/styles/index.scss`의 규칙이 처리한다 (`html.dark`에서 `-light.png` 숨김, 반대는 `-dark.png` 숨김). 이미지 경로가 `/images/study-`로 시작해야 이 규칙에 걸린다.

**스크립트 작성:**
- 위치: `docs/_study/{slug}/_diagrams/{챕터번호}-{이름}.py` — 커밋해서 재생성 가능하게 유지
- 실행: `cd docs/_study/{slug}/_diagrams && python3 {파일}.py`
- 렌더링 후 **두 PNG를 Read로 열어 시각 검증** (겹침·잘림·저대비 확인)
- 색은 반드시 팔레트 키(`P["blue"]` 등)로만 지정 — hex 하드코딩 금지 (라이트/다크 양쪽에서 깨진다)

:::details 스크립트 골격 (_common.diagram 사용)
```python
"""CH{N} §{절} {다이어그램 이름} (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    # 그룹 박스: d.box(x, y, w, h, P["gray"], ec=P["accent"])
    # 노드:     d.box(...) + d.text(cx, cy, "이름\n(부가 1줄)", size=10)
    # 칩(외부): P["chip"], 색 박스: P["blue"|"green"|"brown"|"purple"]
    # 화살표:   d.arrow(x1, y1, x2, y2)  # 기본 accent색
    #           보조 흐름은 color=P["orange"] / P["violet"]
    # 라벨:     d.text(x, y, "라벨", size=8, color=P["dim"])
    ...


diagram("{챕터번호}-{이름}", draw, w=12, h=6, ymax=48)
```
:::

### 4단계: 빌드 및 배포

```bash
cd /Users/hobeen/private/hobeen-kim.github.io
npm run docs:build
git add docs/_study/ docs/.vuepress/public/images/ docs/.vuepress/config.mjs
git commit -m "docs: {챕터명} 내용 보충 — {추가한 내용 요약}"
git push origin master
```

## 삽입 위치 판단 기준

| 상황 | 위치 |
|------|------|
| 기존 절의 내용을 보충 | 해당 절 하단에 추가 |
| 새로운 개념/토픽 | 관련 절 뒤에 새 `##` 절 추가 |
| 실습/예제 추가 | `:::tip 핵심 정리` 바로 위에 삽입 |
| 기존 챕터에 안 맞는 내용 | 사용자에게 새 챕터 생성 여부 확인 |

## 예시 흐름

```
사용자: CAN에서 비트 타이밍이 뭐야?
AI: [비트 타이밍에 대한 상세 설명]
    이 내용을 03. CAN 물리 계층에 추가할까요?
사용자: 응
AI: [03-can-physical.md에 '비트 타이밍' 절 추가]
    [빌드 → 커밋 → 푸시]
    추가 완료. https://hobeen-kim.github.io/study/isobus/03-can-physical 에서 확인 가능합니다.
```

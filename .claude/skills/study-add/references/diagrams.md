# 다이어그램 규칙 (matplotlib → 라이트/다크 PNG 2벌)

Mermaid 대신 matplotlib으로 그려 PNG로 저장하고 마크다운에서 이미지로 참조한다. 테마 전환 시 그림도 함께 바뀌도록 light/dark 두 장을 만든다.

## 스타일 — 가벼운 보조 그림

- 그림에는 구조만 담는다: 노드 이름(+괄호 1줄), 그룹 라벨, 화살표 + 짧은 라벨. 설명은 본문의 몫이다.
- 대제목·부제·하단 요약 문장·본문을 반복하는 박스 안 서브텍스트는 넣지 않는다 — 절 제목과 본문이 그 역할을 한다.
- 범례는 색이 실제로 정보를 구분할 때만 최소로.
- figsize는 내용에 맞춘다(기본 12×6, 복잡하면 14×8 정도까지).
- 챕터당 2개 이상(복잡한 챕터는 3~4개). 시퀀스(시간 흐름), 구조(구성요소 관계), 비교(선택지), 상태 머신이 특히 효과적이다.

## 파일과 경로

| 대상 | 경로 |
|------|------|
| 헬퍼 | `docs/_study/{slug}/_diagrams/_common.py` (`scripts/setup_study.sh`가 복사) |
| 스크립트 | `docs/_study/{slug}/_diagrams/{챕터번호}-{이름}.py` — 커밋해서 재생성 가능하게 |
| 출력 | `docs/.vuepress/public/images/study-{slug}/{챕터번호}-{이름}-light.png` / `-dark.png` |

파일명 접두사를 챕터 번호로 두는 이유: 병렬 집필 에이전트끼리 이름이 겹치지 않고, 어느 챕터 그림인지 바로 보인다. README용은 `readme-` 접두사.

실행: `cd docs/_study/{slug}/_diagrams && python3 {파일}.py` (60초 이내)

## 마크다운 참조

같은 alt 텍스트로 연속 두 줄. alt는 그림 내용을 문장으로 구체적으로 쓴다(검색·접근성).

```md
![후보 수집부터 nomination까지 — 양쪽 에이전트가 STUN Binding으로 후보 쌍을 점검하고 controlling 쪽이 USE-CANDIDATE로 지명하는 흐름](/images/study-{slug}/06-connectivity-check-light.png)
![후보 수집부터 nomination까지 — 양쪽 에이전트가 STUN Binding으로 후보 쌍을 점검하고 controlling 쪽이 USE-CANDIDATE로 지명하는 흐름](/images/study-{slug}/06-connectivity-check-dark.png)
```

테마 전환은 `docs/.vuepress/styles/index.scss`가 처리한다(`html.dark`에서 `-light.png` 숨김, 반대도 마찬가지). 경로가 `/images/study-`로 시작해야 이 규칙에 걸린다.

## 색과 글꼴

- 색은 팔레트 키로만: `bg, text, dim, accent, edge, blue, green, brown, purple, gray, chip, orange, violet`. hex를 하드코딩하면 한쪽 테마에서 깨진다.
- 한글 글꼴(AppleSDGothicNeo 등)에 없는 글리프는 네모로 깨진다. 실제로 깨졌던 것: `✕`, `✓`, `−`(U+2212 마이너스), 이모지. ASCII(`x`, `O`, `-`)나 한글로 대체한다.

## 골격

```python
"""CH{N} §{절} {다이어그램 이름} (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    # 그룹 박스: d.box(x, y, w, h, P["gray"], ec=P["accent"])
    # 노드:     d.box(...) + d.text(cx, cy, "이름\n(부가 1줄)", size=10)
    # 외부 요소: P["chip"], 색 박스: P["blue"|"green"|"brown"|"purple"]
    # 화살표:   d.arrow(x1, y1, x2, y2)            # 기본 accent
    #           d.arrow(..., color=P["orange"], ls="--")  # 보조·대체 경로
    # 라벨:     d.text(x, y, "라벨", size=8, color=P["dim"])


diagram("{챕터번호}-{이름}", draw, w=12, h=6, ymax=48)
```

예시: `docs/_study/observability/_diagrams/05-core-components.py`(구조), `05-data-flow.py`(시퀀스), `docs/_study/webrtc/_diagrams/25-architecture.py`(복잡한 아키텍처), `readme-roadmap.py`(로드맵).

## 시각 검증

렌더 후 Read 도구로 light/dark PNG를 둘 다 열어 본다. 흔히 나오는 문제와 고치는 법:

| 증상 | 처방 |
|------|------|
| 라벨이 화살표·선과 겹침 | 라벨 y를 1~2 단위 띄우거나 화살표 시작점을 옮긴다 |
| 박스 밖으로 글자 넘침·잘림 | 박스 폭을 키우거나 줄바꿈 `\n` |
| 점선이 박스를 관통 | 경로를 꺾어(두 개의 arrow) 우회 |
| 다크에서 글자가 안 보임 | 색 박스 위 텍스트는 기본 `text` 색 유지, `dim`은 배경 위 라벨에만 |
| 네모 글리프 | 위 "색과 글꼴" 참고 |

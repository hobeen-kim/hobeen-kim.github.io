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

### 다이어그램 작성 규칙 (matplotlib → PNG)

새 다이어그램은 Mermaid가 아니라 **matplotlib으로 그려 PNG로 저장**하고 마크다운에서 이미지로 참조한다.

- 스크립트 위치: `docs/_study/{slug}/_diagrams/{챕터번호}-{이름}.py` — 커밋해서 재생성 가능하게 유지
- PNG 출력 위치: `docs/.vuepress/public/images/study-{slug}/{챕터번호}-{이름}.png`
- 마크다운 참조: `![다이어그램 설명](/images/study-{slug}/{챕터번호}-{이름}.png)`
- 실행: `python3 docs/_study/{slug}/_diagrams/{파일}.py` 후 PNG 생성 확인
- 스크립트 필수 패턴:
  - `matplotlib.use("Agg")` — headless 렌더링
  - 한글 폰트 자동 탐색 (`AppleSDGothicNeo` → `NanumGothic` → …) + `axes.unicode_minus = False`
  - 다크 팔레트 (배경 `#0f1216`, 텍스트 `#e6e8eb`, 보조 `#9aa2ab`, 액센트 `#4fd1c5`)
  - `FancyBboxPatch`(둥근 박스) · `FancyArrowPatch`(화살표) · `ax.text` 헬퍼 함수(`box`/`text`/`arrow`)로 구성
  - `ax.axis("off")`, 좌표계는 `ax.set_xlim/set_ylim`으로 논리 그리드 설정
  - 제목 + 부제(dim 색), 하단에 핵심 흐름 요약 한 줄, 필요 시 `Line2D` 범례
  - `fig.savefig(out, dpi=170, facecolor=C_BG)` — dpi 170
- 템플릿: `_diagrams/` 아래 기존 스크립트를 복사해 시작한다. 없으면 아래 골격 사용

:::details matplotlib 다이어그램 스크립트 골격
```python
"""{스터디명} — {다이어그램 제목} (matplotlib → PNG)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D


def set_korean_font():
    avail = {f.name for f in fm.fontManager.ttflist}
    for name in ("AppleSDGothicNeo", "Apple SD Gothic Neo", "AppleGothic",
                 "NanumGothic", "Malgun Gothic", "Noto Sans CJK KR"):
        if name in avail:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


set_korean_font()

C_BG, C_TEXT, C_DIM, C_ACCENT, C_EDGE = "#0f1216", "#e6e8eb", "#9aa2ab", "#4fd1c5", "#5b6570"

fig, ax = plt.subplots(figsize=(15, 9))
fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)
ax.set_xlim(0, 100)
ax.set_ylim(0, 60)
ax.axis("off")


def box(x, y, w, h, fc, ec=C_EDGE, lw=1.4, r=0.03):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={r*20}",
        linewidth=lw, edgecolor=ec, facecolor=fc, mutation_aspect=1))


def text(x, y, s, size=11, color=C_TEXT, weight="normal", ha="center", va="center", style="normal"):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, style=style, zorder=5)


def arrow(x1, y1, x2, y2, color=C_ACCENT, lw=2.0, style="-|>", rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
        mutation_scale=16, linewidth=lw, color=color,
        connectionstyle=f"arc3,rad={rad}", linestyle=ls, zorder=4))


# ---- 제목 ----
text(50, 57.5, "{다이어그램 제목}", size=20, weight="bold")
text(50, 55, "{부제 — 구성 요약}", size=12, color=C_DIM)

# ---- 본문: box/text/arrow 로 구성 ----

# ---- 하단 요약 + 범례 ----
text(50, 2.5, "{핵심 흐름 한 줄 요약}", size=10, color=C_ACCENT, weight="bold")

plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
out = "docs/.vuepress/public/images/study-{slug}/{챕터번호}-{이름}.png"
fig.savefig(out, dpi=170, facecolor=C_BG)
print("saved", out)
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

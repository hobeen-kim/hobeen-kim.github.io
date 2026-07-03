"""CH19 Loki 3계층 — 라벨 / 구조화 메타데이터 / 로그 본문 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 스트림 (상단 중앙)
    d.box(38, 33, 24, 6, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 36, "스트림", size=12, weight="bold", color=P["accent"])

    # 라벨 (좌) — 스트림 식별
    d.box(4, 33, 28, 6, P["green"])
    d.text(18, 37, "라벨", size=11, weight="bold")
    d.text(18, 34.4, "인덱스 · 저카디널리티", size=8.3, color=P["dim"])
    d.arrow(32, 36, 38, 36, color=P["accent"], ls="--")
    d.text(35, 37.6, "식별", size=7.5, color=P["accent"])

    # 두 본문 계층 (하단)
    d.box(10, 18, 38, 10, P["blue"], ec=P["accent"], lw=1.6)
    d.text(29, 24.5, "구조화 메타데이터", size=11.5, weight="bold", color=P["accent"])
    d.text(29, 21, "비인덱스 · 고카디널리티 허용\n파서 불필요", size=9, color=P["dim"])

    d.box(52, 18, 38, 10, P["brown"])
    d.text(71, 24.5, "로그 본문", size=11.5, weight="bold")
    d.text(71, 21, "비인덱스 · 파서 필요", size=9, color=P["dim"])

    d.arrow(46, 33, 33, 28, color=P["orange"])
    d.arrow(54, 33, 67, 28, color=P["orange"])

    # 예시
    d.box(10, 10, 38, 5.4, P["chip"])
    d.text(29, 12.7, "trace_id · user_id · request_id", size=9, color=P["accent"])
    d.box(52, 10, 38, 5.4, P["chip"])
    d.text(71, 12.7, "JSON 필드 · 원문 메시지", size=9, color=P["dim"])


diagram("19-three-layers", draw, w=12, h=5.4, ymax=44)

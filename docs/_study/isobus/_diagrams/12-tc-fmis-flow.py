"""CH12 §9 TC 중심 작업 데이터 흐름: Part 1 6.7.3·6.7.4 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 작업기 네트워크 그룹
    d.box(35.5, 5, 92.5, 42, P["gray"], ec=P["accent"], lw=1.2)
    d.text(38.5, 44, "작업기 네트워크", size=9, weight="bold", color=P["accent"], ha="left")

    # 노드
    d.box(2, 19, 22, 14, P["chip"], ec=P["edge"])
    d.text(13, 26, "FMIS\n(농장 사무실)", size=9.5, weight="bold")
    d.box(38, 19, 22, 14, P["brown"])
    d.text(49, 26, "FMIS 인터페이스\n(게이트웨이)", size=9)
    d.box(72, 19, 18, 14, P["purple"], ec=P["accent"], lw=1.6)
    d.text(81, 26, "TC", size=11, weight="bold")
    d.box(103, 11, 22, 30, P["chip"], ec=P["edge"])
    d.text(114, 37.5, "작업기 CF", size=9, weight="bold")
    for i in range(3):
        d.box(106, 13 + i * 7.3, 16, 5.6, P["green"])
        d.text(114, 15.8 + i * 7.3, f"CF {i + 1}", size=8.5)

    # 흐름: 위쪽 = 내려가는 방향, 아래쪽 = 올라오는 방향
    d.arrow(24, 29.5, 38, 29.5, color=P["accent"], ls="--")
    d.arrow(38, 22.5, 24, 22.5, color=P["orange"], ls="--")
    d.text(29.5, 15.5, "물리 규격\n표준 밖", size=8, color=P["dim"])

    d.arrow(60, 29.5, 72, 29.5, color=P["accent"])
    d.arrow(72, 22.5, 60, 22.5, color=P["orange"])

    d.arrow(90, 29.5, 106, 29.5, color=P["accent"])
    d.arrow(106, 22.5, 90, 22.5, color=P["orange"])

    d.text(29.5, 33.2, "작업\n데이터", size=8, color=P["accent"])
    d.text(66, 33.2, "Part 10\n메시지", size=8, color=P["accent"])
    d.text(98, 33.2, "제어\n메시지", size=8, color=P["accent"])
    d.text(98, 18.6, "측정·\n상태", size=8, color=P["orange"])
    d.text(66, 18.6, "기록\n데이터", size=8, color=P["orange"])
    d.text(81, 13.5, "저장·스케줄·기록", size=8, color=P["dim"])
    d.text(81, 8.5, "데이터 요소: Part 11 DDI", size=8, color=P["dim"])


diagram("12-tc-fmis-flow", draw, w=13, h=5.0, xmax=130, ymax=50)

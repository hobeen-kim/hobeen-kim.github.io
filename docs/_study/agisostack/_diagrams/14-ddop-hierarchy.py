"""CH14 §2 DDOP 오브젝트 계층 — DVC 루트 아래 DET 트리, 각 DET에 DPD/DPT, DVP는 참조."""
from _common import diagram
from matplotlib.patches import Patch


def draw(d):
    P = d.P

    # 루트 Device
    d.box(30, 50, 26, 7, P["blue"])
    d.text(43, 53.5, "DVC  Device \"Isobus Seeder\"", size=9.6, weight="bold")

    # 1단: DET Device
    d.box(30, 39, 26, 7, P["green"])
    d.text(43, 42.5, "DET  Device \"Seeder\"", size=9.2)
    d.arrow(43, 50, 43, 46, color=P["edge"], lw=1.4)

    # 2단
    for x, w, label, sub in ((2, 20, "DET  Connector", "장착 위치"),
                             (28, 30, "DET  Function \"Boom\"", "붐 · 작업 폭 · 섹션 제어 상태"),
                             (62, 22, "DET  Bin \"Product\"", "탱크 · 살포량")):
        d.box(x, 27, w, 7, P["green"])
        d.text(x + w / 2, 31.4, label, size=9.0)
        d.text(x + w / 2, 28.7, sub, size=8.0, color=P["dim"])
        d.arrow(43, 39, x + w / 2, 34, color=P["edge"], lw=1.2)

    # 3단: Section들 (Boom의 자식)
    for i, x in enumerate((24, 38, 52)):
        d.box(x, 16, 13, 6, P["green"])
        d.text(x + 6.5, 19, f"DET  Section {i}", size=8.4)
        d.arrow(43, 27, x + 6.5, 22, color=P["edge"], lw=1.1)

    # DPD / DPT 칩
    d.box(2, 16, 20, 6, P["chip"])
    d.text(12, 19, "DPD  Connector X/Y\nDPT  Connector Type", size=8.0, color=P["dim"])
    d.arrow(12, 27, 12, 22, color=P["edge"], lw=1.0)

    d.box(24, 6, 41, 7, P["chip"])
    d.text(44.5, 9.5,
           "DPT  Offset X · Offset Y · Width\nDPD  Actual Condensed Work State",
           size=8.2, color=P["dim"])
    for x in (30.5, 44.5, 58.5):
        d.arrow(x, 16, x, 13, color=P["edge"], lw=1.0)

    d.box(69, 13, 16, 12, P["chip"])
    d.text(77, 19, "DPD  Bin Level\nDPD  Target Rate\nDPD  Actual Rate\nDPT  Operation Type",
           size=8.0, color=P["dim"])
    d.arrow(77, 27, 77, 25, color=P["edge"], lw=1.0)

    # DVP 컬럼
    d.box(89, 6, 9, 40, P["purple"])
    d.text(93.5, 43, "DVP", size=9.6, weight="bold")
    d.text(93.5, 26, "mm\nm\nm^2\nseeds\nminutes\nseeds/ha", size=8.2)
    d.text(93.5, 9.5, "단위 · 배율\n소수 자릿수", size=8.0, color=P["dim"])
    d.arrow(89, 34, 85, 34, color=P["orange"], lw=1.3)
    d.text(87, 36.5, "참조", size=8.2, color=P["orange"])

    d.legend([
        Patch(facecolor=P["blue"], edgecolor=P["edge"], label="DVC (루트, 1개)"),
        Patch(facecolor=P["green"], edgecolor=P["edge"], label="DET (요소 계층)"),
        Patch(facecolor=P["chip"], edgecolor=P["edge"], label="DPD (런타임 값) · DPT (고정 값)"),
        Patch(facecolor=P["purple"], edgecolor=P["edge"], label="DVP (표시 방법)"),
    ], anchor=(0.005, 0.0))


diagram("14-ddop-hierarchy", draw, w=13.5, h=7.6, ymax=60)

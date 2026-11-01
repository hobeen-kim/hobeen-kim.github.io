"""28장 2절 FMI 신호 범위 영역 a~k와 영역별 FMI (light/dark PNG)."""
from _common import diagram

REGIONS = [
    ("f", "범위 밖\n(low 단락)", "FMI 4 / 5", "gray", 4, 14),
    ("d", "가장 심함", "FMI 1", "purple", 14, 24),
    ("j", "중간", "FMI 18", "brown", 24, 33),
    ("h", "약함", "FMI 17", "blue", 33, 42),
    ("c", "정상", "고장 아님", "green", 42, 58),
    ("i", "약함", "FMI 15", "blue", 58, 67),
    ("k", "중간", "FMI 16", "brown", 67, 76),
    ("e", "가장 심함", "FMI 0", "purple", 76, 86),
    ("g", "범위 밖\n(high 단락)", "FMI 3 / 6", "gray", 86, 96),
]


def brace(d, x1, x2, y, label):
    P = d.P
    d.ax.plot([x1, x1, x2, x2], [y + 1.2, y, y, y + 1.2], color=P["dim"], lw=1.2, zorder=3)
    d.text((x1 + x2) / 2, y - 2.0, label, size=8.8, color=P["dim"])


def draw(d):
    P = d.P
    top = 30
    for letter, meaning, fmi, color, x1, x2 in REGIONS:
        ec = P["orange"] if color == "gray" else None
        d.box(x1, 20, x2 - x1, 9, P[color], ec=ec, lw=1.2, r=0.004)
        d.text((x1 + x2) / 2, 26.8, letter, size=10.5, weight="bold")
        d.text((x1 + x2) / 2, 23.0, meaning, size=8.2)
        fcolor = P["dim"] if letter == "c" else P["accent"]
        d.text((x1 + x2) / 2, top + 2.2, fmi, size=9.2, weight="bold", color=fcolor)

    d.text(28, 39.6, "정상 미만", size=9, color=P["dim"])
    d.text(72, 39.6, "정상 초과", size=9, color=P["dim"])
    d.arrow(41.5, 36.6, 14.5, 36.6, color=P["dim"], lw=1.1)
    d.arrow(58.5, 36.6, 85.5, 36.6, color=P["dim"], lw=1.1)

    d.arrow(3, 16, 98, 16, color=P["edge"], lw=1.2)
    d.text(4, 13.8, "낮은 값", size=8.4, color=P["dim"], ha="left")
    d.text(97, 13.8, "높은 값", size=8.4, color=P["dim"], ha="right")

    brace(d, 14, 86, 9, "b: 물리적으로 가능한 범위")
    brace(d, 4, 96, 3.5, "a: 전자 모듈이 잴 수 있는 전체 범위")


diagram("28-fmi-signal-regions", draw, w=13, h=4.6, xmax=100, ymax=42)

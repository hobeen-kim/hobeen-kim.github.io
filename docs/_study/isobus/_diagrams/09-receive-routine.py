"""CH09 §11 Part 3 Annex A 전형적 수신 루틴 흐름도 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(x, y, w, h, label, kind):
        fc = {"start": P["chip"], "q": P["purple"], "act": P["blue"], "drop": P["gray"]}[kind]
        d.box(x, y, w, h, fc, ec=P["accent"] if kind == "start" else None)
        d.text(x + w / 2, y + h / 2, label, size=8.8)

    def lab(x, y, s, ha="center", color=None):
        d.text(x, y, s, size=8.2, color=color or P["dim"], ha=ha)

    # 열 x: 왼쪽 6~30, 가운데 38~62, 오른쪽 70~94
    node(38, 55, 24, 5.4, "프레임 수신\nPriority 비트는 보지 않는다", "start")
    node(38, 44, 24, 6, "PF = 234 ?\n(Request PGN)", "q")
    node(70, 44, 24, 6, "DA = 255 또는\n내 주소 중 하나?", "q")
    node(70, 33.5, 24, 5.4, "request queue\nID 4 + 데이터 3바이트", "act")
    node(82, 55, 12, 4.4, "무시", "drop")

    node(38, 33, 24, 6, "PF < 240 ?\n(PDU1)", "q")
    node(6, 33, 24, 6, "DA = 255 또는\n내 주소 중 하나?", "q")
    node(6, 23.5, 12, 4.4, "무시", "drop")

    node(38, 21, 24, 6, "관심 PGN ?\n(점프 테이블)", "q")
    node(76, 22, 12, 4.4, "무시", "drop")
    node(38, 9, 24, 6, "SA가 특별\n관심 대상?", "q")
    node(6, 1, 24, 6, "전용 버퍼\n데이터 8바이트", "act")
    node(70, 1, 24, 6, "순환 큐\nID 4 + 데이터 8 = 12바이트", "act")

    # 흐름
    d.arrow(50, 55, 50, 50)
    d.arrow(62, 47, 70, 47)
    lab(66, 48.8, "예")
    d.arrow(82, 44, 82, 38.9)
    lab(83.5, 41.5, "예", ha="left")
    d.arrow(88, 50, 88, 55, color=P["dim"])
    lab(89.5, 52.5, "아니오", ha="left")

    d.arrow(50, 44, 50, 39)
    lab(51.5, 41.5, "아니오", ha="left")
    d.arrow(38, 36, 30, 36)
    lab(34, 37.8, "예")
    d.arrow(12, 33, 12, 27.9, color=P["dim"])
    lab(10.5, 30.5, "아니오", ha="right")
    d.ax.plot([24, 24, 44], [33, 30, 30], color=P["accent"], lw=1.8)
    d.arrow(44, 30, 44, 27)
    lab(25.5, 31.2, "예", ha="left")
    d.arrow(50, 33, 50, 27)
    lab(51.5, 30.5, "아니오 (PDU2)", ha="left")

    d.arrow(62, 24, 76, 24, color=P["dim"])
    lab(69, 25.8, "아니오")
    d.arrow(50, 21, 50, 15)
    lab(51.5, 18, "예", ha="left")
    d.arrow(38, 12, 18, 7)
    lab(27, 11, "예")
    d.arrow(62, 12, 82, 7)
    lab(73, 11, "아니오")


diagram("09-receive-routine", draw, w=11, h=7, xmax=100, ymax=62)

"""CH21 §3.2 SCC 상태 머신: ISO 11783-14 Figure 5 재구성 (light/dark PNG)."""
from _common import diagram


def node(d, cx, cy, w, h, label, fc):
    d.box(cx - w / 2, cy - h / 2, w, h, fc)
    d.text(cx, cy, label, size=10.5, weight="bold")


def draw(d):
    P = d.P

    # Enabled 그룹
    d.box(3, 3, 94, 39, P["gray"], ec=P["accent"], lw=1.2)
    d.text(5, 39.6, "Enabled 상태: SCClientStatus 연속 송신", size=9, color=P["dim"], ha="left")

    # 시동 -> Disabled
    d.ax.plot([18], [53], marker="o", markersize=9, color=P["text"])
    d.arrow(19.2, 53, 40.5, 53)
    d.text(29.8, 55.4, "SCC_A", size=8.5)
    d.text(29.8, 50.8, "Initialization 1회", size=8, color=P["dim"])
    node(d, 50, 53, 18, 5.5, "Disabled", P["chip"])

    node(d, 50, 28, 18, 6, "Ready", P["blue"])
    node(d, 15, 28, 20, 6, "Recording", P["green"])
    node(d, 85, 28, 20, 6, "Play Back", P["brown"])
    node(d, 50, 9, 18, 6, "Abort", P["purple"])

    # Disabled -> Ready
    d.arrow(46, 50.2, 46, 31.1)
    d.text(44.5, 46, "SCC_B", size=8.5, ha="right")

    # Enabled(어디서나) -> Disabled
    d.arrow(56, 42, 56, 50.2, color=P["orange"])
    d.text(57.5, 46.6, "SCC_C / D / E* / F* / G", size=8.5, ha="left", color=P["orange"])
    d.text(57.5, 44, "(Enabled 어느 상태에서나)", size=8, ha="left", color=P["dim"])

    # Ready <-> Recording
    d.arrow(40.9, 29.5, 25.1, 29.5)
    d.text(33, 31.4, "SCC_K", size=8.5)
    d.arrow(25.1, 26.5, 40.9, 26.5)
    d.text(33, 24.4, "SCC_L / M", size=8.5)

    # Ready <-> Play Back
    d.arrow(59.1, 29.5, 74.9, 29.5)
    d.text(67, 31.4, "SCC_N / O", size=8.5)
    d.arrow(74.9, 26.5, 59.1, 26.5)
    d.text(67, 24.4, "SCC_L", size=8.5)

    # Play Back -> Abort
    d.arrow(83, 24.9, 59.1, 10.5)
    d.text(73.5, 14.5, "SCC_R / S / T*", size=8.5, ha="left")

    # Abort -> Ready
    d.arrow(50, 12.1, 50, 24.9)
    d.text(48.5, 18.5, "SCC_L", size=8.5, ha="right")

    d.text(95.5, 4.6, "* 선택(optional) 천이", size=8, color=P["dim"], ha="right")


diagram("21-scc-state-machine", draw, w=12, h=6.6, xmax=100, ymax=60)

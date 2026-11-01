"""CH1 1절 개별 배선과 버스 통신 비교: ECU를 1:1로 이을 때와 버스 하나에 이을 때 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax

    def ecu(cx, cy, label, w=13, h=5.6):
        d.box(cx - w / 2, cy - h / 2, w, h, P["blue"])
        ax.patches[-1].set_zorder(3)
        d.text(cx, cy, label, size=10.5)

    def wire(xs, ys, color, lw):
        ax.plot(xs, ys, color=color, lw=lw, zorder=2)

    # 왼쪽: 개별 배선
    d.box(2, 2, 45, 38, P["gray"])
    d.text(4, 37, "개별 배선 (1:1 연결)", size=11, weight="bold", ha="left")
    pos = {"엔진 ECU": (12.5, 26), "계기판 ECU": (36.5, 26),
           "변속기 ECU": (12.5, 11), "브레이크 ECU": (36.5, 11)}
    names = list(pos)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            (x1, y1), (x2, y2) = pos[names[i]], pos[names[j]]
            wire([x1, x2], [y1, y2], P["orange"], 1.8)
    for name, (x, y) in pos.items():
        ecu(x, y, name)
    d.text(24.5, 4.6, "전선 6가닥", size=10, color=P["dim"])

    # 오른쪽: 버스 통신
    d.box(53, 2, 45, 38, P["gray"])
    d.text(55, 37, "버스 통신 (선로 하나를 함께 씀)", size=11, weight="bold", ha="left")
    by = 18.5
    wire([56, 95], [by, by], P["accent"], 3.2)
    for x, name in ((62, "엔진 ECU"), (75.5, "계기판 ECU"), (89, "변속기 ECU")):
        ecu(x, 28, name, w=12.4)
        wire([x, x], [by, 25.2], P["edge"], 1.6)
    for x, name in ((70, "브레이크 ECU"), (85, "센서 ECU")):
        ecu(x, 9, name, w=12.4)
        wire([x, x], [11.8, by], P["edge"], 1.6)
    d.text(57, by - 3, "통신 버스 선로", size=9.5, color=P["dim"], ha="left")


diagram("01-wiring-compare", draw, w=12, h=4.9, xmax=100, ymax=41)

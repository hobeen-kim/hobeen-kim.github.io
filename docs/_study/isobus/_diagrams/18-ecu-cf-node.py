"""18장 7절: ECU, CF, node의 관계. 주소와 NAME은 CF마다 하나씩 (light/dark PNG)."""
from _common import diagram

BUS_Y = 7


def cf(d, x, w, lines, fc):
    d.box(x, 19, w, 15, fc)
    d.text(x + w / 2, 26.5, lines, size=10)


def attach(d, x, label_side="right"):
    P = d.P
    d.ax.plot([x, x], [BUS_Y, 16], color=P["edge"], lw=1.4, zorder=2)
    d.ax.plot([x], [BUS_Y], marker="o", markersize=8, color=P["text"], zorder=6)
    dx = 1.6 if label_side == "right" else -1.6
    d.text(x + dx, 11.2, "node (접속점)", size=9, color=P["dim"],
           ha="left" if label_side == "right" else "right")


def draw(d):
    P = d.P
    d.ax.plot([3, 97], [BUS_Y, BUS_Y], color=P["accent"], lw=2.8, zorder=2)
    d.text(3, 3.4, "버스 (작업기 네트워크)", size=9.5, weight="bold", color=P["accent"], ha="left")

    d.box(5, 16, 54, 27, P["gray"], ec=P["edge"])
    d.text(32, 39.8, "ECU 6 (케이스 하나)", size=10.5, weight="bold")
    cf(d, 8, 23, "CF: VT\n주소 38\nNAME 1", P["purple"])
    cf(d, 33, 23, "CF: 관리 게이트웨이\n주소 37\nNAME 2", P["purple"])
    attach(d, 32)

    d.box(65, 16, 31, 27, P["gray"], ec=P["edge"])
    d.text(80.5, 39.8, "작업기 컨트롤러 ECU", size=10.5, weight="bold")
    cf(d, 69, 23, "CF: 작업기 제어\n주소 1개\nNAME 1개", P["green"])
    attach(d, 80.5)


diagram("18-ecu-cf-node", draw, w=12, h=5.4, xmax=100, ymax=46)

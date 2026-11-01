"""26장 1절 주소 클레임 흐름: 두 ECU가 같은 주소 128을 원할 때 (light/dark PNG)."""
from _common import diagram

A_X, BUS_X, B_X = 16, 50, 84
TOP = 62


def lifeline(d, x, label, fc):
    P = d.P
    d.box(x - 12, TOP, 24, 7, fc)
    d.text(x, TOP + 3.5, label, size=10, weight="bold")
    d.ax.plot([x, x], [9, TOP], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)


def msg(d, x1, x2, y, label, color=None):
    d.arrow(x1, y, x2, y, color=color or d.P["accent"])
    d.text((x1 + x2) / 2, y + 2.4, label, size=8.8)


def note(d, y, label):
    P = d.P
    d.box(A_X - 8, y - 2.4, (B_X + 8) - (A_X - 8), 4.8, P["chip"], ec=P["orange"])
    d.text(BUS_X, y, label, size=9.2, color=P["orange"])


def draw(d):
    P = d.P
    lifeline(d, A_X, "ECU A\n(NAME: 낮은 값)", P["blue"])
    lifeline(d, BUS_X, "ISOBUS (버스)", P["gray"])
    lifeline(d, B_X, "ECU B\n(NAME: 높은 값)", P["purple"])

    msg(d, A_X, BUS_X, 54, "Request for Address Claimed\nSA=254, 주소 128 조회")
    msg(d, B_X, BUS_X, 54, "Request for Address Claimed\nSA=254, 주소 128 조회")
    note(d, 46.5, "250 ms + RTxD 대기: 응답이 없으면 클레임 진행")
    msg(d, A_X, BUS_X, 38, "Address Claimed (128)\nNAME = 낮은 값")
    msg(d, B_X, BUS_X, 38, "Address Claimed (128)\nNAME = 높은 값")
    note(d, 30.5, "충돌: NAME 수치가 낮은 쪽이 우선권을 얻는다")
    msg(d, A_X, BUS_X, 22, "Address Claimed (128) 재송신\n주소 128 확정")
    msg(d, B_X, BUS_X, 22, "Address Claimed (129)\n다른 빈 주소로 재클레임", color=P["violet"])
    note(d, 14.5, "클레임 후 250 ms 동안 경합이 없어야 성공")


diagram("26-address-claim-flow", draw, w=12, h=7.2, xmax=100, ymax=70)

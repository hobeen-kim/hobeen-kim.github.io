"""CH14 대상 CF 안의 pending NAME과 current NAME: Set Pending, ACK, Adopt, Address Claimed (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 14, 20, 18, P["gray"])
    d.text(12, 23, "서비스 툴\n(commanding CF)\nSA 0x9A", size=9)

    d.box(40, 2, 60, 42, P["blue"])
    d.text(70, 41, "대상 CF B (target CF), SA 0x81", size=9.5, weight="bold")

    d.box(46, 25.5, 48, 11, P["chip"], ec=P["violet"], lw=1.8)
    d.text(70, 34, "pending NAME", size=9.5, weight="bold", color=P["violet"])
    d.text(70, 30.8, "A1 08 82 00 28 03 D0 90", size=10)
    d.text(70, 27.6, "DCI = 1, 채택 전에는 효력 없음", size=8, color=P["dim"])

    d.box(46, 5, 48, 11, P["chip"], ec=P["accent"], lw=1.8)
    d.text(70, 13.5, "current NAME", size=9.5, weight="bold", color=P["accent"])
    d.text(70, 10.3, "A0 08 82 00 28 03 D0 90", size=10)
    d.text(70, 7.1, "DCI = 0, Adopt 전까지 송신에 쓴다", size=8, color=P["dim"])

    d.arrow(70, 25.3, 70, 16.2, color=P["violet"])
    d.text(72, 20.8, "채택", size=8.5, color=P["violet"], ha="left")

    d.arrow(22, 30, 45.8, 30, color=P["accent"])
    d.text(31, 32.6, "① Set Pending\n(Mode 0)", size=8)
    d.arrow(45.8, 27, 22, 27, color=P["dim"], ls="--")
    d.text(31, 24.4, "② ACK\n(Mode 3)", size=8)
    d.arrow(22, 17, 39.8, 17, color=P["violet"])
    d.text(31, 14.4, "③ Adopt\n(Mode 7)", size=8)

    d.box(108, 5, 18, 11, P["gray"])
    d.text(117, 10.5, "다른 CF들\n(Global)", size=9)
    d.arrow(94.2, 10.5, 107.8, 10.5, color=P["accent"])
    d.text(117, 19.6, "④ Address Claimed\n(새 NAME)", size=7.8)


diagram("14-nm-pending-current", draw, w=12.8, h=4.6, xmax=128, ymax=46)

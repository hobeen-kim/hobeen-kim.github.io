"""CH13 Commanded Address 흐름: BAM 전송, NAME 일치 확인, 새 SA로 Address Claimed (light/dark PNG)."""
from _common import diagram


def lifeline(d, x, top, bottom, name):
    P = d.P
    d.box(x - 12, top, 24, 7, P["gray"])
    d.text(x, top + 3.5, name, size=9, weight="bold")
    d.ax.plot([x, x], [bottom, top], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)


def msg(d, x1, x2, y, label):
    d.arrow(x1, y, x2, y)
    d.text((x1 + x2) / 2, y + 2.8, label, size=8.2)


def draw(d):
    P = d.P
    master, bus, ecu = 20, 58, 96
    top, bottom = 48, 2

    lifeline(d, master, top, bottom, "관리 장치\n(예: 진단기)")
    lifeline(d, bus, top, bottom, "CAN 버스")
    lifeline(d, ecu, top, bottom, "대상 ECU\n(NAME=0xABCD)")

    msg(d, master, bus, 40, "Commanded Address (BAM 전송)\nNAME=0xABCD, New SA=0x10")
    msg(d, bus, ecu, 31, "Commanded Address 수신")
    d.box(ecu - 12, 19, 24, 6.5, P["chip"], ec=P["accent"], lw=1.5)
    d.text(ecu, 22.25, "내 NAME(0xABCD)\n일치 확인", size=8.2)
    msg(d, ecu, bus, 11, "Address Claimed\nSA=0x10, NAME=0xABCD")
    d.box(ecu - 12, 2.6, 24, 4.4, P["green"])
    d.text(ecu, 4.8, "SA=0x10으로 변경 완료", size=8.2)


diagram("13-commanded-address-flow", draw, w=12, h=5.6, xmax=120, ymax=56)

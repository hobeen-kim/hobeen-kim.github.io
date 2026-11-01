"""CH13 같은 주소 23을 두 ECU가 클레임할 때의 흐름과 진 쪽의 두 갈래 (light/dark PNG)."""
from _common import diagram


def lifeline(d, x, top, bottom, name):
    P = d.P
    d.box(x - 12, top, 24, 7, P["gray"])
    d.text(x, top + 3.5, name, size=9, weight="bold")
    d.ax.plot([x, x], [bottom, top], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)


def msg(d, x1, x2, y, label, color=None):
    d.arrow(x1, y, x2, y, color=color or d.P["accent"])
    d.text((x1 + x2) / 2, y + 2.8, label, size=8)


def note(d, x0, x1, y0, y1, text, fill, ec=None):
    d.box(x0, y0, x1 - x0, y1 - y0, fill, ec=ec, lw=1.3)
    d.text((x0 + x1) / 2, (y0 + y1) / 2, text, size=8)


def draw(d):
    P = d.P
    a, bus, b = 36, 66, 96
    top, bottom = 88, 3

    lifeline(d, a, top, 38, "ECU A\n(NAME=0x100)")
    lifeline(d, bus, top, bottom, "CAN 버스")
    lifeline(d, b, top, bottom, "ECU B\n(NAME=0x200)")

    note(d, 26, 106, 81.2, 84.8, "전원 ON", P["chip"])
    msg(d, a, bus, 74, "Address Claimed\nSA=23, NAME=0x100")
    msg(d, b, bus, 65, "Address Claimed\nSA=23, NAME=0x200")
    note(d, 56, 76, 56, 60, "SA 충돌 감지", P["chip"], ec=P["orange"])
    msg(d, a, bus, 48, "Address Claimed 재송신\nSA=23, NAME=0x100")
    note(d, 2, 31, 40.5, 51, "상대 0x200 > 내 0x100\n이겼다: 다시 보내\n주소를 지킨다",
         P["green"])
    note(d, 99, 126, 41, 49, "상대 0x100 < 내 0x200\n졌다", P["brown"])

    d.box(24, 3, 103, 34, "none", ec=P["violet"], lw=1.3)
    d.text(25.5, 35.2, "B의 AAC 값에 따라 둘 중 하나", size=8.3, color=P["violet"],
           ha="left", weight="bold")
    d.text(25.5, 31.6, "AAC=1 (자동 재할당 가능)", size=8.3, color=P["violet"], ha="left")
    msg(d, b, bus, 25, "Address Claimed\nSA=128, NAME=0x200")
    note(d, 99, 126, 19.5, 27, "SA=128로 클레임 성공\n(128~247 범위)", P["green"])
    d.ax.plot([24.5, 126.5], [17.5, 17.5], color=P["violet"], lw=1.0, ls=(0, (4, 3)),
              zorder=2)
    d.text(25.5, 15.3, "AAC=0 (자동 재할당 불가)", size=8.3, color=P["violet"], ha="left")
    msg(d, b, bus, 8.5, "Cannot Claim Address\nSA=0xFE", color=P["orange"])
    note(d, 99, 126, 4.5, 11.5, "Null Address로 동작\n(제한적 기능)", P["brown"])


diagram("13-claim-conflict", draw, w=12.4, h=9.0, xmax=128, ymax=96)

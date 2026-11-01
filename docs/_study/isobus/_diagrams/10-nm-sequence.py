"""CH10 §8 NAME management 절차: 지원 확인부터 새 NAME 클레임까지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    tool, cf, others = 16, 66, 112
    top, bottom = 70, 4

    for x, name in ((tool, "서비스 툴\nSA 0x9A"), (cf, "대상 CF B\nSA 0x81"),
                    (others, "다른 CF들\n(Global)")):
        d.box(x - 9, top, 18, 7, P["gray"], ec=P["edge"])
        d.text(x, top + 3.5, name, size=9, weight="bold")
        d.ax.plot([x, x], [bottom, top], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        d.text((x1 + x2) / 2, y + 2.0, label, size=8.2)

    hop(tool, cf, 63, "1. Request (PGN 37632)", P["accent"])
    hop(cf, tool, 56, "2. NM Mode 2: Current NAME", P["dim"], ls="--")
    hop(tool, cf, 49, "3. NM Mode 0: Set Pending (checksum B5)", P["accent"])
    hop(cf, tool, 42, "4. NM Mode 3: NAME ACK", P["dim"], ls="--")

    d.box(cf + 2, 28.5, 24, 8.5, P["chip"], ec=P["orange"], lw=1.2)
    d.text(cf + 14, 32.8, "pending NAME 보관\ncurrent NAME으로 송신 유지", size=8, color=P["orange"])

    d.arrow(tool, 24, cf - 0.6, 24, color=P["violet"])
    d.arrow(cf + 0.6, 24, others, 24, color=P["violet"])
    d.text((tool + cf) / 2, 26.0, "5. NM Mode 7: Adopt (DA=0xFF)", size=8.2)

    d.arrow(cf, 16, others, 16, color=P["accent"])
    d.arrow(cf, 16, tool, 16, color=P["accent"])
    d.text((cf + others) / 2, 18.0, "6. Address Claimed (새 NAME)", size=8.2)

    # 250 ms 후 송신 재개
    bx = cf - 2.0
    d.ax.plot([bx, bx], [5.5, 14.5], color=P["orange"], lw=1.4, zorder=3)
    d.ax.plot([bx, bx + 1.2], [14.5, 14.5], color=P["orange"], lw=1.4, zorder=3)
    d.ax.plot([bx, bx + 1.2], [5.5, 5.5], color=P["orange"], lw=1.4, zorder=3)
    d.text(bx - 1.0, 10.0, "250 ms 후\n송신 재개", size=8, color=P["orange"], ha="right")


diagram("10-nm-sequence", draw, w=12.5, h=6.6, xmax=128, ymax=80)

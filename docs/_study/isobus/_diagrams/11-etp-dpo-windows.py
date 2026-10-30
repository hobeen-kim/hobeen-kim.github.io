"""CH11 §13 4000바이트 ETP 전송의 CTS 창 3개와 DPO 오프셋 (light/dark PNG)."""
from _common import diagram

TOTAL = 572
XL, XR = 6, 96


def px(pkt):
    return XL + (XR - XL) * pkt / TOTAL


def draw(d):
    P = d.P
    bar_y, bar_h = 15, 7
    wins = [
        (1, 255, 0, "blue", "CTS(255, 1)\nDPO(255, 0)"),
        (256, 510, 255, "green", "CTS(255, 256)\nDPO(255, 255)"),
        (511, 572, 510, "brown", "CTS(62, 511)\nDPO(62, 510)"),
    ]
    for a, b, off, color, msg in wins:
        x0, x1 = px(a - 1), px(b)
        d.box(x0, bar_y, x1 - x0, bar_h, P[color])
        d.text((x0 + x1) / 2, bar_y + bar_h / 2, f"패킷 {a}~{b}", size=9.5, weight="bold")
        d.text((x0 + x1) / 2, bar_y + bar_h + 3.4, msg, size=8.6)
        d.text((x0 + x1) / 2, bar_y - 2.6, f"seq 1~{b - a + 1}", size=8.6, color=P["dim"])
        d.text((x0 + x1) / 2, bar_y - 5.4, f"패킷 = {off} + seq", size=8.6, color=P["accent"])

    # hold 표시 (창 1과 창 2 사이)
    hx = px(255)
    d.ax.plot([hx, hx], [bar_y - 7.5, bar_y + bar_h + 6.5], color=P["orange"], lw=1.6, ls=(0, (4, 3)))
    d.text(hx, bar_y + bar_h + 7.6, "CTS(0) hold", size=8.6, color=P["orange"])

    # 바이트 위치 눈금
    for pkt, label in ((0, "Byte 1"), (255, "1785 | 1786"), (510, "3570 | 3571"), (572, "4000")):
        x = px(pkt)
        d.ax.plot([x, x], [bar_y - 9.5, bar_y - 8.3], color=P["edge"], lw=1.2)
        d.text(x, bar_y - 11, label, size=8.2, color=P["dim"])

    # 앞뒤 메시지
    d.text(XL, bar_y + bar_h + 12.5, "RTS (4000 byte)", size=8.8, ha="left", color=P["dim"])
    d.text(XR, bar_y + bar_h + 12.5, "EOMA (4000 byte)", size=8.8, ha="right", color=P["dim"])


diagram("11-etp-dpo-windows", draw, w=12, h=3.3, xmax=100, ymax=36)

"""CH7 3절 CAN FD 듀얼 비트레이트 구간: 각 구간에 들어가는 필드와 속도 (light/dark PNG)."""
from _common import diagram

X0, TOTAL_W = 4, 92
Y, H = 12, 11
SEGS = [
    ("Arbitration phase", "SOF + ID + Control\n(FDF/BRS 포함)", 4, "gray", "Nominal Bit Rate (표준 속도)"),
    ("Data phase", "ESI + DLC + Data + CRC", 6, "blue", "Data Bit Rate (고속)"),
    ("복귀", "CRC Del + ACK\n+ EOF", 2, "gray", "Nominal Bit Rate"),
]


def draw(d):
    P = d.P
    unit = TOTAL_W / sum(s[2] for s in SEGS)
    x = X0
    for name, fields, n, color, rate in SEGS:
        w = n * unit
        is_data = color == "blue"
        d.box(x, Y, w, H, P[color], ec=P["accent"] if is_data else P["edge"], lw=1.8 if is_data else 1.3)
        d.text(x + w / 2, Y + H / 2, fields, size=9.4)
        d.text(x + w / 2, Y + H + 3.0, name, size=10.2, weight="bold",
               color=P["accent"] if is_data else None)
        d.text(x + w / 2, Y - 3.0, rate, size=8.8, color=P["accent"] if is_data else P["dim"],
               weight="bold" if is_data else "normal")
        x += w
    d.arrow(X0, Y - 7.2, X0 + TOTAL_W, Y - 7.2, color=P["edge"], lw=1.2)
    d.text(X0 + TOTAL_W, Y - 9.4, "시간", size=8.4, color=P["dim"], ha="right")


diagram("07-dual-bitrate-phases", draw, w=12, h=3.4, xmax=100, ymax=30)

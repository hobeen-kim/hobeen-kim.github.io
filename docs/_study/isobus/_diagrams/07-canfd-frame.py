"""CH7 §2 CAN FD 프레임 구조 개요 (light/dark PNG)."""
import math

from _common import diagram

# (필드 라벨, 상대 폭 단위, 색상 키, 라벨 높이 레벨 0/1)
FIELDS = [
    ("SOF + Arbitration ID\n(11/29bit)", 11, "blue", 1),
    ("Control\n(IDE·FDF·res·BRS·ESI·DLC)", 4, "green", 0),
    ("Data\n(0~64byte)", 64, "brown", 1),
    ("CRC\n(17 or 21bit)", 15, "purple", 0),
    ("CRC Del\n+ ACK", 2, "chip", 1),
    ("ACK Del\n+ EOF", 2, "gray", 0),
]

X0, TOTAL_W = 3, 94
Y, H = 12, 7


def sqrt_widths(fields, total_w):
    raw = [math.sqrt(n) for _, n, _, _ in fields]
    s = sum(raw)
    return [r / s * total_w for r in raw]


def draw(d):
    P = d.P
    widths = sqrt_widths(FIELDS, TOTAL_W)

    x = X0
    for (name, n, key, lvl), w in zip(FIELDS, widths):
        d.box(x, Y, w, H, P[key])

        ly = Y + H + (1.6 if lvl == 0 else 5.0)
        d.ax.plot([x + 0.12, x + w - 0.12], [ly, ly], color=P["edge"], lw=1.0)
        d.ax.plot([x + 0.12, x + 0.12], [ly - 0.9, ly], color=P["edge"], lw=1.0)
        d.ax.plot([x + w - 0.12, x + w - 0.12], [ly - 0.9, ly], color=P["edge"], lw=1.0)
        d.text(x + w / 2, ly + 1.6, name, size=8.2)

        # Data 필드는 실제 크기(0~64byte)보다 폭을 압축해 그렸음을 표시
        if key == "brown":
            cx = x + w / 2
            for dx in (-0.7, 0.7):
                lx = cx + dx
                d.ax.plot([lx - 0.5, lx + 0.9], [Y + 1.1, Y + H - 1.1],
                          color=P["dim"], lw=1.3)
        x += w

    d.text(X0, Y - 3.0, "Arbitration phase (표준 속도)", size=8.3, color=P["dim"], ha="left")
    d.text(X0 + TOTAL_W, Y - 3.0, "복귀(표준 속도)", size=8.3, color=P["dim"], ha="right")


diagram("07-canfd-frame", draw, w=13, h=5.0, xmax=100, ymax=30)

"""CH4 §3 CAN Extended Data Frame (2.0B, 29bit ID) 필드 배치 (light/dark PNG)."""
import math

from _common import diagram

# (필드 라벨, 비트 수, 색상 키, 라벨 높이 레벨 0/1 — 좁은 인접 필드 겹침 방지)
FIELDS = [
    ("SOF", 1, "chip", 0),
    ("Base ID\n(11bit)", 11, "blue", 1),
    ("SRR", 1, "chip", 0),
    ("IDE=1", 1, "chip", 1),
    ("Extended ID\n(18bit)", 18, "blue", 0),
    ("RTR", 1, "chip", 1),
    ("r1", 1, "chip", 0),
    ("r0", 1, "chip", 1),
    ("DLC\n(4bit)", 4, "green", 0),
    ("Data\n(0~64bit)", 64, "brown", 1),
    ("CRC\n(15bit)", 15, "purple", 0),
    ("CRC\nDel", 1, "chip", 1),
    ("ACK\nSlot", 1, "accent", 0),
    ("ACK\nDel", 1, "chip", 1),
    ("EOF\n(7bit)", 7, "gray", 0),
]

X0, TOTAL_W = 3, 94
Y, H = 12, 6.5


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
        d.ax.plot([x + 0.1, x + w - 0.1], [ly, ly], color=P["edge"], lw=1.0)
        d.ax.plot([x + 0.1, x + 0.1], [ly - 0.9, ly], color=P["edge"], lw=1.0)
        d.ax.plot([x + w - 0.1, x + w - 0.1], [ly - 0.9, ly], color=P["edge"], lw=1.0)
        d.text(x + w / 2, ly + 1.35, name, size=8.0)

        # Data 필드는 실제 비트 수(64bit)보다 폭을 압축해 그렸음을 표시하는 절단 표시
        if key == "brown":
            cx = x + w / 2
            for dx in (-0.7, 0.7):
                lx = cx + dx
                d.ax.plot([lx - 0.5, lx + 0.9], [Y + 1.0, Y + H - 1.0],
                          color=P["dim"], lw=1.3)
        x += w

    d.text(X0, Y - 3.2, "MSB (SOF부터)", size=8.3, color=P["dim"], ha="left")
    d.text(X0 + TOTAL_W, Y - 3.2, "LSB (EOF까지)", size=8.3, color=P["dim"], ha="right")


diagram("04-ext-frame", draw, w=14, h=4.9, xmax=100, ymax=30)

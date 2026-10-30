"""CH04 §8 ISO 11783 식별자 필드가 CEFF·CBFF 프레임 비트에 놓이는 위치 — Part 3 Table 1 (light/dark PNG)."""
from _common import diagram

X0, BW = 10, 2.2          # 프레임 비트 1의 x, 비트 하나 폭

CEFF = [  # (CAN 이름, ISO 11783 이름, 비트 수, 색)
    ("SOF", "SOF", 1, "gray"),
    ("ID28~26", "P3~P1", 3, "blue"),
    ("ID25", "EDP", 1, "purple"),
    ("ID24", "DP", 1, "purple"),
    ("ID23~18", "PF8~PF3", 6, "green"),
    ("SRR", "SRR", 1, "gray"),
    ("IDE", "IDE", 1, "gray"),
    ("ID17~16", "PF2~1", 2, "green"),
    ("ID15~8", "PS8~PS1", 8, "brown"),
    ("ID7~0", "SA8~SA1", 8, "blue"),
    ("RTR", "RTR (d)", 1, "gray"),
    ("FDF", "FDF (d)", 1, "gray"),
    ("r0", "r0", 1, "gray"),
    ("DLC", "DLC4~1", 4, "chip"),
]
CBFF = [
    ("SOF", "SOF", 1, "gray"),
    ("ID28~26", "P3~P1", 3, "blue"),
    ("ID25~18", "SA8~SA1", 8, "blue"),
    ("RTR", "RTR (d)", 1, "gray"),
    ("IDE", "IDE (d)", 1, "gray"),
    ("FDF", "FDF (d)", 1, "gray"),
    ("DLC", "DLC4~1", 4, "chip"),
]


def row(d, y, fields, title):
    P = d.P
    d.text(2, y + 2.5, title, size=9.4, weight="bold", ha="left")
    x, bit = X0, 1
    for can, iso, n, c in fields:
        w = n * BW
        d.box(x, y, w - 0.25, 5, P[c])
        if n >= 2:
            d.text(x + w / 2, y + 2.5, iso, size=7.6)
            d.text(x + w / 2, y + 7.0, can, size=7.0, color=P["dim"])
        else:
            d.ax.text(x + w / 2 - 0.1, y + 2.5, iso, fontsize=6.6, color=P["text"],
                      rotation=90, ha="center", va="center", zorder=5)
            d.ax.text(x + w / 2 - 0.1, y + 8.3, can, fontsize=6.4, color=P["dim"],
                      rotation=90, ha="center", va="center", zorder=5)
        d.text(x + 0.9, y - 1.6, str(bit), size=6.6, color=P["dim"])
        x += w
        bit += n
    d.text(x - 0.9, y - 1.6, str(bit - 1), size=6.6, color=P["dim"])
    return x


def draw(d):
    P = d.P
    row(d, 23, CEFF, "CEFF")
    row(d, 5, CBFF, "CBFF")
    # PF가 SRR·IDE로 갈라지는 지점
    pf_a0 = X0 + 6 * BW
    pf_a1 = pf_a0 + 6 * BW
    pf_b0 = pf_a1 + 2 * BW
    pf_b1 = pf_b0 + 2 * BW
    yb = 20
    d.ax.plot([pf_a0, pf_a1 - 0.3], [yb, yb], color=P["accent"], lw=1.6)
    d.ax.plot([pf_b0, pf_b1 - 0.3], [yb, yb], color=P["accent"], lw=1.6)
    d.ax.plot([pf_a1 - 0.3, pf_b0], [yb, yb], color=P["accent"], lw=1.2, ls=(0, (2, 2)))
    d.text((pf_a0 + pf_b1) / 2, yb - 1.7, "PF 8비트", size=8, color=P["accent"])


diagram("04-iso-id-bit-mapping", draw, w=12.5, h=3.9, xmax=100, ymax=36)

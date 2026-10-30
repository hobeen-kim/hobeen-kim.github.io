"""CH18 §8 태스크 시간 기록 수준 비교 (Part 10 Figure G.1 재구성, light/dark PNG)."""
from _common import diagram

X0, X1 = 20, 96
SEGMENTS = [
    ("Preliminary", "(2)", 10, "blue"),
    ("Effective", "(4)", 15, "green"),
    ("Ineffective", "(5)", 8, "gray"),
    ("Effective", "(4)", 15, "green"),
    ("Ineffective", "(5)", 8, "gray"),
    ("Effective", "(4)", 11, "green"),
    ("Clearing", "(7)", 9, "brown"),
]


def draw(d):
    P = d.P
    for x, label in ((X0, "태스크 시작"), (X1, "태스크 정지")):
        d.ax.plot([x, x], [3, 21.5], color=P["edge"], lw=1.0, ls="--", zorder=0.5)
        d.text(x, 23, label, size=9.5, weight="bold")

    d.text(9, 16, "1. Minimal", size=10.5, weight="bold")
    d.box(X0, 13.5, X1 - X0, 5, P["green"])
    d.text((X0 + X1) / 2, 16, "Effective (4)", size=9.5)

    d.text(9, 6.5, "2. Intermediate", size=10.5, weight="bold")
    x = X0
    for name, code, width, color in SEGMENTS:
        d.box(x, 4, width, 5, P[color])
        d.text(x + width / 2, 6.5, f"{name}\n{code}", size=8.3)
        x += width


diagram("18-time-registration-levels", draw, w=12, h=4.2, xmax=100, ymax=25)

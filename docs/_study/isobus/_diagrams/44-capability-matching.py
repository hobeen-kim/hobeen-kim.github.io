"""44장 Version 메시지로 서로의 능력을 알리고, 물리 섹션 12개를 TC가 다룰 수 있는 6개로 묶어 DDOP에 보고하는 예 (light/dark PNG)."""
from _common import diagram


def card(d, x, y, w, h, title, lines, color):
    P = d.P
    d.box(x, y, w, h, P[color])
    d.text(x + w / 2, y + h - 2.6, title, size=10.5, weight="bold")
    for i, s in enumerate(lines):
        d.text(x + w / 2, y + h - 6.2 - i * 3.0, s, size=8.8)


def draw(d):
    P = d.P
    card(d, 3, 31, 40, 14, "TC의 자기소개 (Version 메시지)",
         ["버전 4 · TC-BAS · TC-SC", "섹션 제어 붐 1 · 섹션 6"], "green")
    card(d, 57, 31, 40, 14, "클라이언트의 자기소개 (Version 메시지)",
         ["버전 4 · TC-BAS · TC-SC", "붐 1 · 섹션 12 (줄이기 전 능력 그대로)"], "blue")
    d.arrow(43.3, 39, 56.7, 39, style="<|-|>", lw=1.6, color=P["edge"])
    d.text(50, 41.3, "서로 교환", size=8.4, color=P["dim"])

    x0, sw, y_phys = 8, 7, 6
    for i in range(12):
        d.box(x0 + i * sw + 0.25, y_phys, sw - 0.5, 4.6, P["chip"])
        d.text(x0 + i * sw + sw / 2, y_phys + 2.3, str(i + 1), size=8.4, color=P["dim"])
    d.text(x0 - 1, y_phys + 2.3, "물리 섹션", size=8.6, ha="right", color=P["dim"])

    y_dd = 14.5
    for g in range(6):
        gx = x0 + g * 2 * sw
        d.box(gx + 0.25, y_dd, 2 * sw - 0.5, 5, P["brown"])
        d.text(gx + sw, y_dd + 2.5, f"DDOP 섹션 {g + 1}", size=8.6)
        d.ax.plot([gx + sw / 2, gx + sw / 2], [y_phys + 4.6, y_dd], color=P["edge"], lw=1.0, zorder=0.8)
        d.ax.plot([gx + 1.5 * sw, gx + 1.5 * sw], [y_phys + 4.6, y_dd], color=P["edge"], lw=1.0, zorder=0.8)
    d.text(x0 - 1, y_dd + 2.5, "DDOP 보고", size=8.6, ha="right", color=P["dim"])

    d.arrow(23, 30.8, 23, 20.2, color=P["orange"], lw=1.6)
    d.text(25, 25.3, "TC가 다룰 수 있는 6개에 맞춰 이웃한 2개씩 묶는다", size=8.6,
           color=P["orange"], ha="left")


diagram("44-capability-matching", draw, w=12, h=5.6, xmax=100, ymax=47)

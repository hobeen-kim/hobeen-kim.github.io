"""41장 Section Control(겹쳐 뿌리지 않기)과 Rate Control(위치마다 양 바꾸기) 비교 (light/dark PNG)."""
from matplotlib.colors import to_rgba
from matplotlib.patches import Rectangle

from _common import diagram


def rect(d, x, y, w, h, fc, ec=None, lw=1.2, z=2):
    d.ax.add_patch(Rectangle((x, y), w, h, facecolor=fc,
                             edgecolor=ec or d.P["edge"], linewidth=lw, zorder=z))


def flow(d, x0, y, labels):
    P = d.P
    x = x0
    for i, (label, w) in enumerate(labels):
        d.box(x, y, w, 5.2, P["chip"])
        d.text(x + w / 2, y + 2.6, label, size=8.6)
        if i < len(labels) - 1:
            d.arrow(x + w + 0.3, y + 2.6, x + w + 3.2, y + 2.6, lw=1.5)
        x += w + 3.5


def section_panel(d):
    P = d.P
    d.text(3, 57.5, "Section Control: 겹쳐 뿌리지 않기", size=11.5, weight="bold", ha="left")
    flow(d, 3, 48.5, [("GPS 위치", 9.5), ("TC-Server", 11), ("Section 1, 2 ON · 3 OFF", 19)])

    rect(d, 4, 10, 42, 34, P["gray"])
    rect(d, 25, 10, 21, 34, P["green"], lw=0)
    d.text(38, 40.5, "이미 살포된 구역", size=9, weight="bold")
    rect(d, 7, 10, 18, 15.6, to_rgba(P["accent"], 0.22), lw=0)
    d.text(16, 12.5, "이번에 뿌린 곳", size=8.6)

    for i, on in enumerate((True, True, False)):
        rect(d, 7 + i * 9, 25.6, 9, 2.4, P["accent"] if on else P["edge"], ec=P["text"], lw=1.0)
        d.text(11.5 + i * 9, 21.2, f"Section {i + 1}\n3 m · {'ON' if on else 'OFF'}", size=8.4,
               color=P["text"] if on else P["dim"])

    rect(d, 17.5, 29.2, 6, 5.6, P["brown"], ec=P["text"], lw=1.0, z=3)
    d.text(20.5, 32, "트랙터", size=7.6)
    d.ax.plot([20.5, 20.5], [28.0, 29.2], color=P["text"], lw=1.2, zorder=3)
    d.arrow(20.5, 35.4, 20.5, 40.6, lw=1.6)
    d.text(22, 38.6, "진행 방향", size=8.4, color=P["accent"], ha="left")

    d.arrow(7, 7, 34, 7, style="<|-|>", lw=1.1, color=P["dim"])
    d.text(20.5, 4.2, "살포기 9 m 폭 · 3구획 (구획마다 3 m)", size=8.6, color=P["dim"])


def rate_panel(d):
    P = d.P
    d.text(53, 57.5, "Rate Control: 위치마다 양 바꾸기", size=11.5, weight="bold", ha="left")
    flow(d, 53, 48.5, [("GPS 위치", 9.5), ("TC-Server", 11), ("목표량 Setpoint", 15)])

    rates = [[100, 150, 200],
             [150, 200, 250],
             [100, 150, 150]]
    alpha = {100: 0.10, 150: 0.24, 200: 0.38, 250: 0.52}
    cw, ch = 14, 34 / 3
    for r, row in enumerate(rates):
        for c, rate in enumerate(row):
            x, y = 54 + c * cw, 10 + (2 - r) * ch
            rect(d, x, y, cw, ch, P["bg"])
            rect(d, x, y, cw, ch, to_rgba(P["accent"], alpha[rate]))
            here = (r, c) == (1, 1)
            d.text(x + cw / 2, y + ch - 2.6 if here else y + ch / 2, f"{rate} L/ha",
                   size=9.2, weight="bold" if here else "normal")
    rect(d, 54 + cw, 10 + ch, cw, ch, (0, 0, 0, 0), ec=P["orange"], lw=2.6)

    rect(d, 54 + cw * 1.5 - 3, 10 + ch + 1.6, 6, 4.6, P["brown"], ec=P["text"], lw=1.0, z=3)
    d.text(54 + cw * 1.5, 10 + ch + 3.9, "트랙터", size=7.6)

    d.text(75, 6.2, "주황 테두리: 트랙터가 지금 있는 칸", size=8.6, color=P["orange"])
    d.text(75, 3.0, "색이 진할수록 처방 맵의 목표량이 많다", size=8.6, color=P["dim"])


def draw(d):
    section_panel(d)
    rate_panel(d)


diagram("41-section-rate-control", draw, w=12, h=7.1, xmax=100, ymax=60)

"""38장: Button을 520 ms 눌렀을 때의 Button Activation 프레임과 TAN, 응답 유실 뒤 재시도 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    X0, X1 = 15, 92
    T_MAX = 900

    def tx(t):
        return X0 + (X1 - X0) * t / T_MAX

    AXIS = 20
    d.arrow(X0, AXIS, X1 + 5, AXIS, color=P["edge"], lw=1.4)
    d.text(X1 + 5, AXIS + 1.6, "시간", size=9, color=P["dim"], ha="right")
    for t in (0, 200, 400, 520, 820):
        d.ax.plot([tx(t), tx(t)], [AXIS - 0.8, AXIS + 0.8], color=P["edge"], lw=1.2)
        d.text(tx(t), AXIS - 2.4, f"{t} ms", size=9, color=P["dim"])

    d.box(tx(0), 36, tx(520) - tx(0), 3.6, P["green"], lw=1.1)
    d.text((tx(0) + tx(520)) / 2, 37.8, "운전자가 누르고 있는 동안", size=9.2)

    d.text(1, 28, "VT가\n보내는 프레임", size=9, color=P["text"], ha="left", weight="bold")
    d.text(1, 12.5, "Working Set의\n응답", size=9, color=P["text"], ha="left", weight="bold")

    frames = [
        (0, "pressed", "TAN 1", P["accent"], True),
        (200, "still held", "TAN 2", P["accent"], True),
        (400, "still held", "TAN 3", P["accent"], True),
        (520, "released", "TAN 4", P["accent"], False),
        (820, "released(재시도)", "TAN 4", P["orange"], True),
    ]
    for t, label, tan, color, answered in frames:
        x = tx(t)
        d.arrow(x, AXIS + 1.2, x, 34, color=color, lw=1.8)
        d.text(x + 0.9, 30.0, label, size=9, color=color, weight="bold", ha="left")
        d.text(x + 0.9, 26.8, tan, size=8.8, color=color, ha="left")
        if answered:
            d.arrow(x + 1.2, 16.0, x + 1.2, 11.5, color=P["dim"], lw=1.2, ls="--")
            d.text(x + 2.0, 13.6, "응답", size=8.5, color=P["dim"], ha="left")
        else:
            d.text(x + 1.2, 13.6, "응답 유실", size=8.8, color=P["orange"], weight="bold", ha="left")

    d.ax.plot([tx(520), tx(820)], [6.4, 6.4], color=P["violet"], lw=1.3)
    d.ax.plot([tx(520), tx(520)], [6.4, 7.4], color=P["violet"], lw=1.3)
    d.ax.plot([tx(820), tx(820)], [6.4, 7.4], color=P["violet"], lw=1.3)
    d.text((tx(520) + tx(820)) / 2, 3.8, "300 ms 동안 응답이 없어 같은 데이터·같은 TAN으로 다시 보냄",
           size=9, color=P["violet"])


diagram("38-button-hold-timeline", draw, w=12.5, h=5.8, xmax=100, ymax=42)

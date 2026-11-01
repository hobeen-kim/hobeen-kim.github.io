"""40장: v6 AUX 입력 잠금의 네 단계와 Status Byte 8의 Bit 2(잠김)·Bit 3(잠긴 중 조작 감지) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    W, H, Y = 21, 22, 14
    xs = [2, 27, 52, 77]
    states = [
        ("1. 평상시", ["조작구를 움직이면", "Value가 따라간다"], "Bit 2 = 0, Bit 3 = 0", P["green"], "Value 변함"),
        ("2. 잠김", ["Value가 잠근 순간의", "값(예: 50 %)에 고정"], "Bit 2 = 1, Bit 3 = 0", P["blue"], "Value 고정"),
        ("3. 잠긴 채 조작", ["Value는 그대로 50 %", "조작했다는 표시만 켜짐"], "Bit 2 = 1, Bit 3 = 1", P["purple"],
         "26 05 00 80 7D FF FF 0C"),
        ("4. 잠금 해제", ["Value가 다시", "조작을 따라간다"], "Bit 2 = 0, Bit 3 = 0", P["green"], "Value 변함"),
    ]
    for x, (title, lines, bits, fc, foot) in zip(xs, states):
        d.box(x, Y, W, H, fc, lw=1.4)
        d.text(x + W / 2, Y + H - 3.2, title, size=10, weight="bold")
        d.text(x + W / 2, Y + H - 9.0, lines[0], size=8.8)
        d.text(x + W / 2, Y + H - 11.6, lines[1], size=8.8)
        d.box(x + 1.5, Y + 2.0, W - 3, 4.4, P["chip"], ec=P["accent"], lw=1.1)
        d.text(x + W / 2, Y + 4.2, bits, size=8.8, color=P["accent"], weight="bold")
        d.text(x + W / 2, Y - 3.0, foot, size=8.4, color=P["dim"])

    labels = ["잠금 스위치 켬", "조작구를 건드림", "잠금 해제"]
    for i, lab in enumerate(labels):
        x1 = xs[i] + W + 0.3
        x2 = xs[i + 1] - 0.3
        d.arrow(x1, Y + H / 2, x2, Y + H / 2, color=P["orange"], lw=1.8)
        d.text((x1 + x2) / 2, Y + H + 2.6, lab, size=8.8, color=P["orange"])
        d.ax.plot([(x1 + x2) / 2, (x1 + x2) / 2], [Y + H / 2 + 0.8, Y + H + 1.2],
                  color=P["orange"], lw=0.8, ls=(0, (2, 2)))


diagram("40-aux-lock-states", draw, w=12.5, h=5.0, xmax=100, ymax=42)

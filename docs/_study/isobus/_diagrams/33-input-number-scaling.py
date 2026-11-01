"""CH33 §5 Input Number 표시값·입력값 변환 (light/dark PNG)."""
from _common import diagram

BH = 8


def node(d, x, y, w, title, sub, color):
    P = d.P
    d.box(x, y, w, BH, P[color])
    d.text(x + w / 2, y + BH / 2 + 1.5, title, size=9.2, weight="bold")
    d.text(x + w / 2, y + BH / 2 - 1.6, sub, size=8.6, color=P["dim"])


def draw(d):
    P = d.P
    y1, y2 = 24, 7

    d.text(3, y1 + BH + 2.6, "화면에 보여 줄 때", size=9, color=P["accent"], ha="left",
           weight="bold")
    node(d, 3, y1, 20, "Number Variable 23", "원시값 2500", "blue")
    node(d, 31, y1, 30, "(Value + Offset) × Scale", "(2500 + 0) × 0.01", "chip")
    node(d, 69, y1, 18, "화면 표시", "25.00", "green")
    d.arrow(23, y1 + BH / 2, 31, y1 + BH / 2)
    d.arrow(61, y1 + BH / 2, 69, y1 + BH / 2)

    d.text(3, y2 + BH + 2.6, "운전자가 값을 넣을 때", size=9, color=P["orange"], ha="left",
           weight="bold")
    node(d, 3, y2, 15, "운전자 입력", "32.5", "green")
    node(d, 23, y2, 20, "범위 확인", "0 ≤ 32.5 ≤ 50", "chip")
    node(d, 48, y2, 25, "입력값 ÷ Scale - Offset", "32.5 ÷ 0.01 - 0", "chip")
    node(d, 78, y2, 19, "Number Variable 23", "3250", "blue")
    d.arrow(18, y2 + BH / 2, 23, y2 + BH / 2, color=P["orange"])
    d.arrow(43, y2 + BH / 2, 48, y2 + BH / 2, color=P["orange"])
    d.arrow(73, y2 + BH / 2, 78, y2 + BH / 2, color=P["orange"])

    d.text(33, y2 - 2.6, "Min 0 → (0 + 0) × 0.01 = 0,  Max 5000 → (5000 + 0) × 0.01 = 50",
           size=8.2, color=P["dim"])
    d.text(87.5, y2 - 2.6, "VT가 Working Set에 보고", size=8.2, color=P["dim"])


diagram("33-input-number-scaling", draw, w=14, h=5.18, xmax=100, ymax=37)

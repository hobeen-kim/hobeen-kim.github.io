"""38장: 매크로 안의 Execute Macro를 즉시 호출할 때와 큐 뒤에 붙일 때 Input Number 값이 달라지는 과정 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def column(x0, title, title_color, steps, final, final_color):
        d.text(x0 + 21, 50.5, title, size=11, weight="bold", color=title_color)
        d.text(x0 + 37.5, 46.2, "0x0028 값", size=8.8, color=P["dim"])
        y = 41
        for i, (label, value, color) in enumerate(steps):
            d.box(x0, y - 3, 31, 6, P[color], lw=1.2)
            d.text(x0 + 15.5, y, label, size=9.2)
            d.box(x0 + 33, y - 3, 9, 6, P["chip"], lw=1.0)
            d.text(x0 + 37.5, y, value, size=10, weight="bold")
            if i < len(steps) - 1:
                d.arrow(x0 + 15.5, y - 3.2, x0 + 15.5, y - 4.8, color=P["edge"], lw=1.2)
            y -= 8
        d.arrow(x0 + 15.5, y + 4.8, x0 + 15.5, 9.4, color=P["edge"], lw=1.2)
        d.box(x0, 3, 42, 6, P["gray"], ec=final_color, lw=2.0)
        d.text(x0 + 21, 6, final, size=10.5, weight="bold", color=final_color)

    column(2, "올바른 VT: 그 자리에서 호출", P["accent"], [
        ("매크로 A 시작", "?", "blue"),
        ("Execute Macro B → B를 바로 실행", "", "purple"),
        ("B: Change Numeric Value = 2", "2", "purple"),
        ("A로 돌아와 Change Numeric Value = 4", "4", "blue"),
    ], "최종값 4", P["accent"])

    column(52, "잘못된 VT: 큐 뒤에 붙임", P["orange"], [
        ("매크로 A 시작", "?", "blue"),
        ("Execute Macro B → 큐 뒤에 붙임", "", "brown"),
        ("A: Change Numeric Value = 4", "4", "blue"),
        ("A가 끝난 뒤 B: Change Numeric Value = 2", "2", "brown"),
    ], "최종값 2", P["orange"])


diagram("38-macro-call-order", draw, w=13, h=6.6, xmax=100, ymax=53)

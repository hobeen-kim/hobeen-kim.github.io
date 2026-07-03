"""CH33 UI 전용 관리 vs as-code 관리 비교 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ---- 위: UI 전용 ----
    d.box(4, 27, 92, 12, P["brown"], ec=P["orange"], lw=1.6)
    d.text(9, 37.4, "UI 전용 관리", size=12, weight="bold", color=P["orange"], ha="left")
    ui = [(26, "클릭으로 패널 수정"), (50, "변경 이력 없음"), (74, "재현 불가")]
    for x, t in ui:
        d.box(x - 10, 29.5, 20, 4.6, P["chip"])
        d.text(x, 31.8, t, size=10)
    d.arrow(36, 31.8, 40, 31.8, color=P["orange"], lw=1.9)
    d.arrow(60, 31.8, 64, 31.8, color=P["orange"], lw=1.9)

    # ---- 아래: as-code ----
    d.box(4, 6, 92, 15, P["green"], ec=P["accent"], lw=1.8)
    d.text(9, 19.4, "as-code 관리", size=12, weight="bold", color=P["accent"], ha="left")
    code = [
        (18, "jsonnet/JSON\n수정"),
        (40, "Git PR 리뷰"),
        (62, "CI가 Grafana에\n반영"),
        (84, "롤백 = git revert"),
    ]
    for x, t in code:
        d.box(x - 9.5, 9.5, 19, 5.2, P["chip"])
        d.text(x, 12.1, t, size=9.5)
    for i in range(len(code) - 1):
        x1 = code[i][0] + 9.5
        x2 = code[i + 1][0] - 9.5
        d.arrow(x1, 12.1, x2, 12.1, color=P["accent"], lw=2.2)


diagram("33-ui-vs-ascode", draw, w=13, h=6, ymax=44)

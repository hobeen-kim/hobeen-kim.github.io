"""44장 TC 번호(function instance + 1)와 클라이언트가 다른 TC로 옮기는 순서 (light/dark PNG)."""
from _common import diagram


def node(d, x, y, w, h, title, sub, color, size=10.5):
    d.box(x, y, w, h, d.P[color])
    if sub:
        d.text(x + w / 2, y + h / 2 + 1.6, title, size=size, weight="bold")
        d.text(x + w / 2, y + h / 2 - 1.7, sub, size=8.4)
    else:
        d.text(x + w / 2, y + h / 2, title, size=size)


def draw(d):
    P = d.P
    node(d, 2, 33, 19, 10, "TC 번호 1 (primary)", "function instance 0", "green", size=10)
    node(d, 25, 33, 19, 10, "TC 번호 2", "function instance 1", "green", size=10)
    node(d, 12, 6, 22, 9, "TC 클라이언트", "", "blue", size=11)

    d.arrow(19, 15.2, 11.5, 32.8)
    d.text(9.5, 22, "지금 연결", size=8.6, color=P["accent"])
    d.arrow(27, 15.2, 34.5, 32.8, color=P["orange"], ls="--")
    d.text(37.5, 22, "Next Task\nController", size=8.6, color=P["orange"])

    steps = [
        "1. 안전 상태로 전환 (아니면 기능을 막는다)",
        "2. 현재 TC에 Connection Deactivate\n    응답을 기다린다 (최대 2 s)",
        "3. 현재 TC로 보내던 Client Task 중단",
        "4. 새 TC와 초기화 → preferred TC로 저장",
    ]
    x, w, h = 53, 45, 7.2
    ys = [35.5, 26, 16.5, 7]
    for i, (y, label) in enumerate(zip(ys, steps)):
        d.box(x, y, w, h, P["chip"])
        d.text(x + 2, y + h / 2, label, size=8.8, ha="left")
        if i < len(steps) - 1:
            d.arrow(x + w / 2, y - 0.2, x + w / 2, ys[i + 1] + h + 0.2, lw=1.5)
    d.text(x + w / 2, 45, "다른 TC로 옮겨 가는 순서", size=9.4, color=P["orange"], weight="bold")


diagram("44-tc-switch", draw, w=12, h=5.6, xmax=100, ymax=47)

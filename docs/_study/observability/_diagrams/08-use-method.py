"""CH08 USE 방법론 — 리소스 기반 자원 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(3, 14, 20, 12, P["brown"], ec=P["violet"], lw=1.8)
    d.text(13, 21.4, "리소스", size=12, weight="bold", color=P["violet"])
    d.text(13, 17.6, "CPU · 메모리 · 디스크\n네트워크 · 커넥션 풀", size=9, color=P["text"])

    outs = [
        (32, "Utilization", "사용 중인 시간의 비율"),
        (20, "Saturation", "처리 못해 쌓인 초과 작업량"),
        (8, "Errors", "자원 자체의 에러 (I/O·OOM·거부)"),
    ]
    for yc, t, sub in outs:
        d.box(52, yc - 4.5, 44, 9, P["blue"])
        d.text(55, yc + 1.4, t, size=12, weight="bold", color=P["accent"], ha="left")
        d.text(55, yc - 1.8, sub, size=9, color=P["text"], ha="left")
        d.arrow(23, 20, 52, yc, color=P["orange"], rad=0.05)


diagram("08-use-method", draw, w=12, h=5.6, ymax=40)

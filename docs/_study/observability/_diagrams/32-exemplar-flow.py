"""CH32 exemplar — 메트릭에서 트레이스로 점프하는 순서 흐름 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    lanes = [
        (13, "애플리케이션", P["gray"]),
        (38, "Prometheus", P["brown"]),
        (63, "Grafana", P["blue"]),
        (88, "Tempo", P["green"]),
    ]
    top_y, bot_y = 45, 5
    X = {}
    for x, name, fc in lanes:
        d.box(x - 9, 45.5, 18, 4.2, fc)
        d.text(x, 47.6, name, size=11, weight="bold")
        d.ax.plot([x, x], [bot_y, top_y], color=P["edge"], lw=1.0, ls="--", zorder=1)
        X[name] = x

    def msg(y, a, b, label, dashed=False, color=None):
        ls = "--" if dashed else "-"
        x1, x2 = X[a], X[b]
        d.arrow(x1, y, x2, y, color=color or P["accent"], lw=1.9, ls=ls)
        d.text((x1 + x2) / 2, y + 1.3, label, size=8, color=P["dim"])

    def note(y, lane, label, w=22):
        x = X[lane]
        d.box(x - w / 2, y - 1.8, w, 3.6, P["chip"], ec=P["orange"], lw=1.1)
        d.text(x, y, label, size=8, color=P["orange"])

    msg(41, "애플리케이션", "Prometheus", "히스토그램 + exemplar(trace_id)", color=P["orange"])
    note(35.5, "Prometheus", "exemplar-storage에\n별도 보관")
    msg(29.5, "Grafana", "Prometheus", "PromQL 쿼리")
    msg(24.5, "Prometheus", "Grafana", "시계열 + exemplar 포인트", dashed=True, color=P["dim"])
    note(19, "Grafana", "그래프 위\n작은 점으로 렌더링")
    msg(13, "Grafana", "Tempo", "점 클릭 → trace_id 조회", color=P["accent"])
    msg(8, "Tempo", "Grafana", "트레이스 반환", dashed=True, color=P["dim"])

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.4, label="exemplar 저장 경로"),
        Line2D([0], [0], color=P["accent"], lw=2.4, label="클릭 → 트레이스 점프"),
        Line2D([0], [0], color=P["dim"], lw=2.4, ls="--", label="응답(반환)"),
    ], loc="lower right", anchor=(0.995, 0.02))


diagram("32-exemplar-flow", draw, w=13, h=7.5, ymax=52)

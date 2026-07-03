"""CH32 통합 drill-down 워크플로우 — 대시보드→트레이스→로그→프로파일 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    lanes = [
        (10, "SRE", P["gray"]),
        (31, "RED 대시보드", P["blue"]),
        (50, "Tempo", P["green"]),
        (70, "Loki", P["brown"]),
        (90, "Pyroscope", P["purple"]),
    ]
    top_y, bot_y = 50, 8
    X = {}
    for x, name, fc in lanes:
        d.box(x - 9, 51, 18, 4.2, fc)
        d.text(x, 53.1, name, size=10.5, weight="bold")
        d.ax.plot([x, x], [bot_y, top_y], color=P["edge"], lw=1.0, ls="--", zorder=1)
        X[name] = x

    def msg(y, a, b, label, dashed=False, color=None):
        ls = "--" if dashed else "-"
        x1, x2 = X[a], X[b]
        d.arrow(x1, y, x2, y, color=color or P["accent"], lw=1.9, ls=ls)
        d.text((x1 + x2) / 2, y + 1.2, label, size=8, color=P["dim"])

    msg(47, "SRE", "RED 대시보드", "p99 레이턴시 스파이크")
    msg(43, "RED 대시보드", "SRE", "exemplar 점 표시", dashed=True, color=P["dim"])
    msg(38.5, "SRE", "Tempo", "exemplar 클릭 → 트레이스")
    msg(34.5, "Tempo", "SRE", "느린 span (DB 호출)", dashed=True, color=P["dim"])
    msg(30, "SRE", "Loki", '"Logs for this span"')
    msg(26, "Loki", "SRE", "에러 로그 없음", dashed=True, color=P["dim"])
    msg(21.5, "SRE", "Pyroscope", '"Profiles for this span"')
    msg(17.5, "Pyroscope", "SRE", "GC 시간 비중 급증", dashed=True, color=P["dim"])

    d.box(4, 10.5, 34, 4.4, P["green"], ec=P["accent"], lw=1.4)
    d.text(21, 12.7, "근본 원인 = GC 압박", size=10, color=P["accent"], weight="bold")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.4, label="클릭 → 다음 신호로 점프"),
        Line2D([0], [0], color=P["dim"], lw=2.4, ls="--", label="결과 반환"),
    ], loc="lower right", anchor=(0.995, 0.02))


diagram("32-drilldown-workflow", draw, w=13, h=8, ymax=56)

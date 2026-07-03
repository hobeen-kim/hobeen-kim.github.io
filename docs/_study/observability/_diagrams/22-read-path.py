"""CH22 읽기 경로 — trace by ID 조회 시퀀스 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    lanes = [(10, "Grafana", "blue"), (30, "Query Frontend", "green"),
             (50, "Querier", "orange"), (70, "Ingester", "brown"),
             (89, "오브젝트 스토리지", "purple")]

    TOP, BOT = 44, 5
    X = {}
    for x, name, c in lanes:
        d.box(x - 9, TOP, 18, 3.6, P[c])
        d.text(x, TOP + 1.8, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [BOT, TOP], color=P["edge"], lw=1.2, ls=(0, (3, 3)), zorder=1)
        X[name] = x

    def msg(a, b, y, label, color, ls="-"):
        d.arrow(X[a], y, X[b], y, color=color, lw=1.9, ls=ls)
        d.text((X[a] + X[b]) / 2, y + 1.1, label, size=8, color=color)

    msg("Grafana", "Query Frontend", 40, "trace_id 조회", P["accent"])
    msg("Query Frontend", "Querier", 36, "조회 위임", P["accent"])
    msg("Querier", "Ingester", 32, "최근 데이터 (메모리)", P["accent"])
    msg("Querier", "오브젝트 스토리지", 28, "bloom filter 확인", P["accent"])
    d.text(70, 23.5, "가능성 있는 블록만 다운로드", size=8, color=P["orange"], style="italic")
    msg("오브젝트 스토리지", "Querier", 19, "블록 parquet", P["dim"], ls=(0, (4, 3)))
    msg("Ingester", "Querier", 15, "최근 span", P["dim"], ls=(0, (4, 3)))
    msg("Querier", "Query Frontend", 11, "trace 병합", P["dim"], ls=(0, (4, 3)))
    msg("Query Frontend", "Grafana", 7, "완성된 trace", P["dim"], ls=(0, (4, 3)))

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.0, label="조회 요청"),
        Line2D([0], [0], color=P["dim"], lw=2.0, ls="--", label="응답 · 병합"),
    ], loc="center left", anchor=(0.02, 0.42))


diagram("22-read-path", draw, w=13, h=6, ymax=50)

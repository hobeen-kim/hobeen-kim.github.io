"""CH35 Mimir 쿼리 경로 — query-frontend 분할·캐시부터 결과 병합까지 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    lanes = [
        (8, "Grafana", P["gray"]),
        (25, "query-\nfrontend", P["purple"]),
        (43, "querier", P["purple"]),
        (61, "ingester", P["blue"]),
        (78, "store-\ngateway", P["green"]),
        (93, "오브젝트\n스토리지", P["brown"]),
    ]
    top_y, bot_y = 51, 7
    X = {}
    for x, name, fc in lanes:
        d.box(x - 7, 51, 14, 4.6, fc)
        d.text(x, 53.3, name, size=9, weight="bold")
        d.ax.plot([x, x], [bot_y, top_y], color=P["edge"], lw=1.0, ls="--", zorder=1)
        X[name] = x

    def msg(y, a, b, label, dashed=False, color=None, up=True):
        ls = "--" if dashed else "-"
        x1, x2 = X[a], X[b]
        d.arrow(x1, y, x2, y, color=color or P["accent"], lw=1.8, ls=ls)
        d.text((x1 + x2) / 2, y + (1.2 if up else -1.6), label, size=8, color=P["dim"])

    def selfmsg(y, lane, label):
        x = X[lane]
        d.box(x - 8, y - 1.6, 24, 3.2, P["chip"], ec=P["orange"], lw=1.1)
        d.text(x + 4, y, label, size=8, color=P["orange"])

    msg(48, "Grafana", "query-\nfrontend", "PromQL 쿼리 (최근 30일)", color=P["violet"])
    selfmsg(43.5, "query-\nfrontend", "일 단위 분할 · 캐시 확인")
    msg(38.5, "query-\nfrontend", "querier", "캐시 미스 구간만 병렬 전달", color=P["violet"])
    msg(33.5, "querier", "ingester", "최근 데이터 조회")
    msg(28.5, "querier", "store-\ngateway", "과거 데이터 조회")
    msg(23.5, "store-\ngateway", "오브젝트\n스토리지", "필요한 청크만 lazy load")
    msg(18.5, "오브젝트\n스토리지", "store-\ngateway", "청크 반환", dashed=True, color=P["dim"], up=False)
    msg(14.5, "store-\ngateway", "querier", "결과 반환", dashed=True, color=P["dim"], up=False)
    msg(10.5, "ingester", "querier", "결과 반환", dashed=True, color=P["dim"], up=False)
    msg(6.5, "querier", "query-\nfrontend", "병합된 결과", dashed=True, color=P["dim"], up=False)

    d.legend([
        Line2D([0], [0], color=P["violet"], lw=2.4, label="분할·분배"),
        Line2D([0], [0], color=P["accent"], lw=2.4, label="데이터 조회"),
        Line2D([0], [0], color=P["dim"], lw=2.4, ls="--", label="결과 반환"),
    ], loc="lower right", anchor=(0.995, 0.015))


diagram("35-query-path", draw, w=15, h=8.4, ymax=57)

"""CH05 §4 데이터 흐름 — scrape → WAL → head → query 시퀀스 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    actors = [
        (8,  "타깃",        P["green"]),
        (25, "Retrieval",   P["blue"]),
        (42, "WAL",         P["brown"]),
        (59, "Head Block",  P["purple"]),
        (76, "영속 블록",   P["gray"]),
        (92, "PromQL 엔진", P["chip"]),
    ]

    # scrape 루프 박스 (뒤 배경)
    d.box(2, 21.5, 69, 18, P["chip"], ec=P["accent"], lw=1.2)
    d.text(7, 38.5, "loop: scrape_interval 마다", size=8.5, color=P["accent"],
           ha="left", style="italic")

    # 라이프라인
    for x, name, col in actors:
        ec = P["accent"] if name == "PromQL 엔진" else P["edge"]
        d.box(x - 7.5, 41, 15, 5, col, ec=ec, lw=1.5)
        d.text(x, 43.5, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [5, 41], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        d.text((x1 + x2) / 2, y + 1.4, label, size=8, color=color)

    hop(25, 8, 34.5, "GET /metrics", P["accent"])
    hop(8, 25, 31, "샘플 응답", P["dim"], ls="--")
    hop(25, 42, 27.5, "append (durability)", P["orange"])
    d.arrow(25, 24, 59, 24, color=P["violet"])
    d.text(42, 25.4, "동시에 메모리 청크 append", size=8, color=P["violet"])

    hop(59, 76, 17, "기본 2h flush", P["orange"])
    d.text(50, 13.2, "flush 후 대응 WAL 세그먼트 truncate", size=8, color=P["dim"])

    hop(92, 59, 10, "최근 조회", P["accent"])
    hop(92, 76, 6.5, "과거 조회", P["accent"])

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.4, label="동기 호출"),
        Line2D([0], [0], color=P["dim"], lw=2.4, ls="--", label="응답 반환"),
    ])


diagram("05-data-flow", draw, w=13, h=6.6, ymax=48)

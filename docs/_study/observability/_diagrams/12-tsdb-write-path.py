"""CH12 로컬 TSDB 쓰기 경로 — head block·WAL·mmap·block (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 스크레이프 샘플 (top center)
    d.box(40, 40, 20, 6, P["orange"])
    d.text(50, 43, "스크레이프 샘플", size=11, weight="bold")

    # WAL (left)
    d.box(8, 26, 24, 8, P["brown"])
    d.text(20, 31, "WAL", size=12, weight="bold")
    d.text(20, 28.2, "(디스크, append-only)", size=9, color=P["dim"])

    # Head Block (right)
    d.box(54, 24, 30, 11, P["green"], ec=P["accent"], lw=1.8)
    d.text(69, 31, "Head Block", size=12, weight="bold", color=P["accent"])
    d.text(69, 27.5, "(메모리 · 최근 ~2h)", size=9.5, color=P["dim"])

    # mmap chunk (bottom right)
    d.box(54, 8, 30, 9, P["gray"])
    d.text(69, 13.5, "mmap chunk", size=11, weight="bold")
    d.text(69, 10.5, "(디스크 매핑 · 페이지 캐시)", size=9, color=P["dim"])

    # 불변 Block (bottom left)
    d.box(8, 8, 24, 9, P["blue"])
    d.text(20, 13.5, "불변 Block", size=11, weight="bold")
    d.text(20, 10.5, "(chunks + index + meta)", size=9, color=P["dim"])

    # 샘플 -> WAL / Head
    d.arrow(44, 40, 26, 34, color=P["orange"], rad=0.1)
    d.text(31, 39, "append", size=8, color=P["orange"])
    d.arrow(56, 40, 66, 35, color=P["orange"], rad=-0.1)
    d.text(64, 39, "append", size=8, color=P["orange"])

    # Head -> mmap
    d.arrow(69, 24, 69, 17, color=P["accent"])
    d.text(77, 20.5, "chunk가 차면", size=8, color=P["accent"])

    # Head -> Block (flush)
    d.arrow(54, 27, 32, 14, color=P["accent"], rad=0.14)
    d.text(43, 22.5, "2h 완료 시 flush", size=8, color=P["accent"])

    # WAL -> Head (replay)
    d.arrow(20, 34, 54, 30, color=P["violet"], rad=-0.18)
    d.text(37, 36.4, "재시작 시 replay", size=8, color=P["violet"])

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="샘플 append"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="디스크 flush / mmap"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="WAL replay (복구)"),
    ])


diagram("12-tsdb-write-path", draw, w=12, h=6, ymax=48)

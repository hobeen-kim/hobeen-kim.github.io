"""CH27 플레임그래프 읽는 법 — 스택 + 값을 가로 막대 스택으로 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    X0, W100 = 6.0, 88.0
    BH = 7.0

    def X(pct):
        return X0 + pct * (W100 / 100.0)

    def frame(start_pct, width_pct, level, label, pct, fc, ec=None):
        y = 12 + level * (BH + 1.6)
        x = X(start_pct)
        w = width_pct * (W100 / 100.0)
        d.box(x, y, w, BH, fc, ec=ec or P["edge"], lw=1.4)
        cx = x + w / 2
        if width_pct >= 12:
            d.text(cx, y + BH * 0.60, label, size=10, weight="bold")
            d.text(cx, y + BH * 0.26, f"{pct}%", size=9, color=P["accent"])
        else:
            d.text(cx, y + BH * 0.60, label, size=8, weight="bold")
            d.text(cx, y + BH * 0.24, f"{pct}%", size=7.5, color=P["accent"])

    frame(0, 100, 0, "main", 100, P["gray"], ec=P["accent"])
    frame(0, 95, 1, "handleRequest", 95, P["blue"])
    frame(0, 40, 2, "parseJSON", 40, P["green"])
    frame(40, 50, 2, "dbQuery", 50, P["brown"])
    frame(90, 5, 2, "writeLog", 5, P["purple"])
    frame(40, 30, 3, "encodeRow", 30, P["orange"])
    frame(70, 20, 3, "acquireConn", 20, P["purple"])

    # y축 (스택 깊이)
    d.arrow(3.2, 12, 3.2, 12 + 3 * (BH + 1.6) + BH, color=P["dim"], lw=1.6)
    d.ax.text(1.8, 12 + 2 * (BH + 1.6), "스택 깊이 (y축)", fontsize=9,
              color=P["dim"], rotation=90, ha="center", va="center", zorder=5)
    d.text(50, 8, "◀  집계 비중 (x축) — 너비 넓을수록 리소스 소비 큼  ▶",
           size=9, color=P["dim"])


diagram("27-flamegraph-tree", draw, w=13, h=6, ymax=52)

"""CH4 분할 전략 비교 — KFold vs GroupKFold vs TimeSeriesSplit (light/dark PNG).

각 전략을 폴드 격자로 표현한다. 파란 칸=train, 주황 칸=validation,
회색 칸=미사용(TimeSeriesSplit의 미래 구간). 잘못된 분할이 leakage의
1순위 원인임을 한눈에 대비시키는 것이 목적이다.
"""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    train, val, unused = P["blue"], P["orange"], P["chip"]

    cw, chh, step = 6.0, 3.0, 6.4
    x0 = 30

    def cells(top, colors):
        for i, c in enumerate(colors):
            d.box(x0 + i * step, top, cw, chh, c, lw=0.8)

    def panel(title, title_top, rows, fold_labels, group_header=None):
        d.text(2, title_top, title, size=11, weight="bold", ha="left")
        y = title_top - 3.4
        if group_header:
            for i, g in enumerate(group_header):
                d.text(x0 + i * step + cw / 2, y + 1.4, g, size=8.5,
                       color=P["dim"])
            y -= 3.4
        for r, colors in enumerate(rows):
            yy = y - r * (chh + 0.6)
            d.text(x0 - 2, yy + chh / 2, fold_labels[r], size=8,
                   color=P["dim"], ha="right")
            cells(yy, colors)
        return yy  # 마지막 행의 bottom

    # --- KFold (k=4, 12 samples) ---
    n = 12
    kf = []
    per = n // 4
    for f in range(4):
        row = [train] * n
        for j in range(f * per, (f + 1) * per):
            row[j] = val
        kf.append(row)
    y = panel("KFold — 무작위 균등 분할", 66,
              kf, [f"Fold {i+1}" for i in range(4)])

    # --- GroupKFold (같은 그룹은 통째로 한 폴드에) ---
    groups = [c // 3 for c in range(n)]  # 4 그룹 x 3
    gk = []
    for f in range(4):
        gk.append([val if groups[c] == f else train for c in range(n)])
    header = ["A", "A", "A", "B", "B", "B", "C", "C", "C", "D", "D", "D"]
    y = panel("GroupKFold — 같은 유저(그룹)는 분리 금지", y - 4.5,
              gk, [f"Fold {i+1}" for i in range(4)], group_header=header)

    # --- TimeSeriesSplit (확장 윈도우, 미래는 미사용) ---
    ts = []
    for f in range(4):
        te = 4 + f * 2
        row = [unused] * n
        for j in range(te):
            row[j] = train
        for j in range(te, te + 2):
            row[j] = val
        ts.append(row)
    y = panel("TimeSeriesSplit — 과거로 학습, 미래로 검증", y - 4.5,
              ts, [f"Fold {i+1}" for i in range(4)])

    d.text(30, y - 3.5, "시간 →", size=8.5, color=P["dim"], ha="left")

    handles = [
        Line2D([0], [0], marker="s", linestyle="none", markersize=10,
               markerfacecolor=train, markeredgecolor=P["edge"], label="train"),
        Line2D([0], [0], marker="s", linestyle="none", markersize=10,
               markerfacecolor=val, markeredgecolor=P["edge"], label="validation"),
        Line2D([0], [0], marker="s", linestyle="none", markersize=10,
               markerfacecolor=unused, markeredgecolor=P["edge"], label="미사용"),
    ]
    d.legend(handles, loc="lower right", anchor=(0.99, 0.02))


diagram("04-cv-strategies", draw, w=11, h=9.5, ymax=68)

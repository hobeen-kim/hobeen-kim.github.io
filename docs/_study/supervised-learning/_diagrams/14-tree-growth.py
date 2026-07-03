"""level-wise(XGBoost) vs leaf-wise(LightGBM) 트리 성장 비교 (light/dark PNG)."""
from _common import diagram


def _node(d, x, y, fc, ec=None, r=1.7):
    P = d.P
    d.box(x - r, y - r, 2 * r, 2 * r, fc, ec=ec or P["edge"], lw=1.4, r=0.06)


def _edge(d, x1, y1, x2, y2, color=None):
    d.arrow(x1, y1 - 1.7, x2, y2 + 1.7, color=color or d.P["edge"],
            lw=1.4, style="-")


def draw(d):
    P = d.P

    # ── 왼쪽: level-wise (같은 깊이를 균등하게) ──
    cx = 25
    d.text(cx, 46, "level-wise (XGBoost 기본)", size=11, weight="bold")
    lv = [
        [(cx, 38)],
        [(cx - 9, 27), (cx + 9, 27)],
        [(cx - 13, 16), (cx - 5, 16), (cx + 5, 16), (cx + 13, 16)],
    ]
    fills = [P["blue"], P["blue"], P["green"]]
    for depth in range(1, len(lv)):
        for i, (x, y) in enumerate(lv[depth]):
            px, py = lv[depth - 1][i // 2]
            _edge(d, px, py, x, y)
    for depth, row in enumerate(lv):
        for (x, y) in row:
            _node(d, x, y, fills[depth])
    d.text(cx, 8, "모든 노드를 같은 깊이로 확장\n→ 균형 트리, max_depth로 제어",
           size=9, color=P["dim"])

    # ── 오른쪽: leaf-wise (손실 감소 큰 잎만 깊게) ──
    cx = 75
    d.text(cx, 46, "leaf-wise (LightGBM 기본)", size=11, weight="bold")
    root = (cx, 38)
    n1l, n1r = (cx - 9, 27), (cx + 9, 27)
    n2l, n2r = (cx - 14, 16), (cx - 4, 16)
    n3l, n3r = (cx - 17, 5), (cx - 11, 5)
    edges = [(root, n1l), (root, n1r), (n1l, n2l), (n1l, n2r),
             (n2l, n3l), (n2l, n3r)]
    # 확장이 이어진 경로 강조
    hot = {n1l, n2l}
    for a, b in edges:
        _edge(d, *a, *b, color=P["accent"] if b in hot or b in (n3l, n3r) else P["edge"])
    _node(d, *root, P["blue"])
    _node(d, *n1l, P["blue"], ec=P["accent"])
    _node(d, *n1r, P["green"])
    _node(d, *n2l, P["blue"], ec=P["accent"])
    _node(d, *n2r, P["green"])
    _node(d, *n3l, P["green"])
    _node(d, *n3r, P["green"])
    d.text(cx, 46, "", size=1)
    d.text(76, 33, "손실 감소가\n가장 큰 잎 선택", size=8, color=P["accent"], ha="left")
    d.text(cx, 8, "비대칭·깊게 성장 → 표현력 ↑, 과적합 ↑\nnum_leaves로 제어",
           size=9, color=P["dim"])


diagram("14-tree-growth", draw, w=12, h=5.4, xmax=100, ymax=50)

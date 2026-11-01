"""CH45 §3 살포기 Element 계층: Device 아래 Function·Bin, Function 아래 Section 3개 (light/dark PNG)."""
from _common import diagram

BW, BH = 18, 10

NODES = {  # 키: (중심 x, 중심 y, 글자, 색)
    "dev": (58, 40, "Device\n살포기 전체\n(Element 0)", "blue"),
    "func": (40, 24, "Function\n살포 펌프\n(Element 1)", "purple"),
    "bin": (80, 24, "Bin\n약액 탱크\n(Element 2)", "brown"),
    "s1": (20, 8, "Section\n왼쪽 섹션\n(Element 3)", "green"),
    "s2": (40, 8, "Section\n가운데 섹션\n(Element 4)", "green"),
    "s3": (60, 8, "Section\n오른쪽 섹션\n(Element 5)", "green"),
}
EDGES = [("dev", "func"), ("dev", "bin"), ("func", "s1"), ("func", "s2"), ("func", "s3")]


def draw(d):
    P = d.P
    for x, y, label, color in NODES.values():
        d.box(x - BW / 2, y - BH / 2, BW, BH, P[color])
        d.text(x, y, label, size=10)
    for a, b in EDGES:
        xa, ya = NODES[a][:2]
        xb, yb = NODES[b][:2]
        d.arrow(xa, ya - BH / 2 - 0.2, xb, yb + BH / 2 + 0.2, color=P["accent"])


diagram("45-element-tree", draw, w=12, h=5.6, xmax=100, ymax=47)

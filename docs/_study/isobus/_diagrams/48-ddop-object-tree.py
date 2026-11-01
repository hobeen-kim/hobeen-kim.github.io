"""48장 2절: DDOP 다섯 오브젝트의 나무 구조, 섹션 3개로 줄인 예 (light/dark PNG)."""
from _common import diagram

TYPE_COLOR = {"DVC": "purple", "DET": "blue", "DPD": "green", "DPT": "brown", "DVP": "gray"}
H = 8.0

# key: (x, y, w, type, 둘째·셋째 줄)
NODES = {
    "dvc": (38, 50, 24, "DVC", "Device\n살포기 전체, NAME, S/N"),
    "root": (38, 37, 24, "DET", "type = Device\n전체 기능 루트"),
    "s1": (7, 24, 22, "DET", "type = Section\nSection 1 (3 m)"),
    "s2": (33, 24, 22, "DET", "type = Section\nSection 2 (3 m)"),
    "s3": (59, 24, 22, "DET", "type = Section\nSection 3 (3 m)"),
    "dpt": (83, 24, 16, "DPT", "작업 폭\n값 = 9 m"),
    "sp": (0.5, 11, 17, "DPD", "DDI 1\nSetpoint Vol/Area"),
    "ms": (19, 11, 17, "DPD", "DDI 2\nActual Vol/Area"),
    "dvp": (9, 0.8, 19, "DVP", "단위 L/ha\nScale 0.0001"),
}


def top(k):
    x, y, w, _, _ = NODES[k]
    return x + w / 2, y + H


def bottom(k):
    x, y, w, _, _ = NODES[k]
    return x + w / 2, y


def draw(d):
    P = d.P
    for k, (x, y, w, kind, label) in NODES.items():
        d.box(x, y, w, H, P[TYPE_COLOR[kind]])
        d.text(x + w / 2, y + H - 1.7, kind, size=8.6, weight="bold")
        d.text(x + w / 2, y + (H - 2.6) / 2, label, size=7.0)

    def link(a, b, dx_a=0.0, dx_b=0.0):
        (x1, y1), (x2, y2) = bottom(a), top(b)
        d.arrow(x1 + dx_a, y1, x2 + dx_b, y2, color=P["dim"], lw=1.3)

    link("dvc", "root")
    for k, dx in (("s1", -6), ("s2", -2), ("s3", 2), ("dpt", 6)):
        link("root", k, dx_a=dx)
    link("s1", "sp", dx_a=-3)
    link("s1", "ms", dx_a=3)
    link("sp", "dvp", dx_b=-3)
    link("ms", "dvp", dx_b=3)

    for k in ("s2", "s3"):
        x, y, w, _, _ = NODES[k]
        d.text(x + w / 2, y - 3.2, "(아래 DPD는 그림에서 생략)", size=6.8, color=P["dim"])


diagram("48-ddop-object-tree", draw, w=12, h=7.0, xmax=100, ymax=59.5)

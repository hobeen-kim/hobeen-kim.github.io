"""CH16 §5 오브젝트 풀 계층 구조 (Working Set → Data Mask → 자식 오브젝트) (light/dark PNG)."""
from _common import diagram

# (라벨, 타입 라벨, 색상 키, 들여쓰기 레벨, 부모 인덱스)
NODES = [
    ("Working Set", "ID 0", "blue", 0, None),
    ("Data Mask", "ID 1", "green", 1, 0),
    ("Output String", "ID 10", "brown", 2, 1),
    ("Output Number", "ID 11", "brown", 2, 1),
    ("Font Attributes", "ID 30", "purple", 3, 2),
    ("Font Attributes", "ID 30", "purple", 3, 3),
]

SUBLABEL = {
    0: None,
    1: "Active Data Mask",
    2: '"엔진 온도:" 레이블',
    3: "85 (°C)",
    4: "검정, 24×32px",
    5: "공유 사용",
}

X_STEP = 20
BW, BH = 16, 6.4


def draw(d):
    P = d.P
    centers = {}
    # 명시적 좌표 배치 (트리 형태를 시각적으로 정확히 맞추기 위해)
    pos = {
        0: (4, 18),                 # Working Set
        1: (4 + X_STEP, 18),        # Data Mask
        2: (4 + X_STEP * 2, 27),    # Output String
        3: (4 + X_STEP * 2, 9),     # Output Number
        4: (4 + X_STEP * 3, 27),    # Font Attributes (String)
        5: (4 + X_STEP * 3, 9),     # Font Attributes (Number)
    }
    for i, (label, sub, color, lvl, parent) in enumerate(NODES):
        x, y = pos[i]
        centers[i] = (x + BW / 2, y + BH / 2)
        d.box(x, y, BW, BH, P[color])
        d.text(x + BW / 2, y + BH / 2 + 1.1, label, size=9.5, weight="bold")
        d.text(x + BW / 2, y + BH / 2 - 1.1, sub, size=8, color=P["dim"])
        extra = SUBLABEL.get(i)
        if extra:
            d.text(x + BW / 2, y - 1.8, extra, size=8, color=P["dim"])

    for i, (_, _, _, _, parent) in enumerate(NODES):
        if parent is None:
            continue
        px, py = pos[parent]
        cx, cy = pos[i]
        x1, y1 = px + BW, py + BH / 2
        x2, y2 = cx, cy + BH / 2
        d.arrow(x1, y1, x2, y2, color=P["dim"], lw=1.4, style="-|>")


diagram("16-object-pool-tree", draw, w=14, h=6, xmax=90, ymax=38)

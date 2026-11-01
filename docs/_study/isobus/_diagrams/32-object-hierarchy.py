"""CH32 §3 오브젝트 간 계층 관계 예시 (light/dark PNG)."""
from _common import diagram, Line2D

BW, BH = 15, 6.5

# key: (중심 x, 상자 아래 y, 이름, 보조 라벨, 색 키)
NODES = {
    "WS": (55, 51, "Working Set Object", "ID 0", "blue"),
    "DM1": (36, 38.5, "Data Mask 1", "일반 작업 화면", "green"),
    "DM2": (70, 38.5, "Data Mask 2", "설정 화면", "green"),
    "AM": (88, 38.5, "Alarm Mask", "경고 화면", "green"),
    "SKM": (17.5, 26, "Soft Key Mask", "소프트키 집합", "purple"),
    "BTN": (36, 26, "Button", "'확인'", "purple"),
    "CON": (58.5, 26, "Container", "온도 정보 그룹", "gray"),
    "SK1": (9, 13.5, "Key 1", "'시작'", "purple"),
    "SK2": (26, 13.5, "Key 2", "'정지'", "purple"),
    "ON": (50, 13.5, "Output Number", "85°C", "brown"),
    "OS": (67, 13.5, "Output String", "'엔진 온도'", "brown"),
    "FA": (58.5, 1, "Font Attributes", "글꼴 정의", "chip"),
}

# (부모, 자식, 참조 여부)
EDGES = [
    ("WS", "DM1", False), ("WS", "DM2", False), ("WS", "AM", False),
    ("DM1", "SKM", True), ("DM1", "BTN", False), ("DM1", "CON", False),
    ("SKM", "SK1", False), ("SKM", "SK2", False),
    ("CON", "ON", False), ("CON", "OS", False),
    ("ON", "FA", True), ("OS", "FA", True),
]


def draw(d):
    P = d.P
    for cx, y, name, sub, color in NODES.values():
        d.box(cx - BW / 2, y, BW, BH, P[color])
        d.text(cx, y + BH / 2 + 1.2, name, size=9.5, weight="bold")
        d.text(cx, y + BH / 2 - 1.4, sub, size=8.5, color=P["dim"])

    for parent, child, is_ref in EDGES:
        px, py = NODES[parent][0], NODES[parent][1]
        cx, cy = NODES[child][0], NODES[child][1]
        d.arrow(px, py, cx, cy + BH, color=P["dim"] if not is_ref else P["orange"],
                lw=1.4, ls="--" if is_ref else "-")

    d.legend([
        Line2D([0], [0], color=P["dim"], lw=1.4, label="자식으로 담는다"),
        Line2D([0], [0], color=P["orange"], lw=1.4, ls="--", label="속성으로 가리킨다(참조)"),
    ], fontsize=9)


diagram("32-object-hierarchy", draw, w=14, h=8.4, xmax=100, ymax=60)

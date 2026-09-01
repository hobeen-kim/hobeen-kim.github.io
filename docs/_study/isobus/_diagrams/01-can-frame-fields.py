"""CH1 §5 CAN 프레임 구조 — SOF/ID/DLC/데이터/CRC/ACK/EOF 필드와 각 역할 (light/dark PNG)."""
from _common import diagram

FIELDS = [
    # (라벨, 폭, 색상키, 역할)
    ("SOF", 9, "gray", "시작"),
    ("ID\n(29bit)", 15, "blue", "식별"),
    ("DLC", 10, "gray", "길이"),
    ("데이터\n(0~8byte)", 25, "green", "페이로드"),
    ("CRC", 13, "brown", "오류검출"),
    ("ACK", 9, "gray", "확인"),
    ("EOF", 9, "gray", "종료"),
]


def draw(d):
    P = d.P
    x = 2.0
    gap = 1.3
    box_y, box_h = 17, 11
    for label, w, color_key, role in FIELDS:
        d.box(x, box_y, w, box_h, P[color_key], ec=P["edge"], lw=1.3)
        d.text(x + w / 2, box_y + box_h / 2, label, size=10.5, weight="bold")
        # 필드 → 역할 연결 화살표 (아래에서 위로)
        d.arrow(x + w / 2, 11.5, x + w / 2, box_y - 0.3,
                color=P["dim"], lw=1.3, style="-|>")
        d.text(x + w / 2, 8.5, role, size=9.5, color=P["dim"])
        x += w + gap


diagram("01-can-frame-fields", draw, w=13, h=4.6, xmax=100, ymax=32)

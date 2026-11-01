"""CH32 §6 Font Attributes(ID 30) 레코드 8바이트 풀어 읽기 (light/dark PNG)."""
from _common import diagram

UNIT = 11.0
X0 = 6
CELL_Y, CELL_H = 10, 7

# (바이트, 바이트 수, 필드 이름, 읽은 값, 오프셋, 색 키)
FIELDS = [
    ("1E 00", 2, "Object ID", "30\n(00 1E로 읽음)", "0~1", "blue"),
    ("17", 1, "Type", "23 =\nFont Attributes", "2", "blue"),
    ("00", 1, "글자 색", "0 = 검정", "3", "green"),
    ("06", 1, "글자 크기", "6 =\n24×32 픽셀", "4", "green"),
    ("00", 1, "Font type", "0 = ISO 8859-1\n(가정)", "5", "green"),
    ("00", 1, "글자 스타일", "0 = 일반", "6", "green"),
    ("00", 1, "매크로 개수", "0 = 없음", "7", "brown"),
]


def draw(d):
    P = d.P
    x = X0
    for hexs, n, name, value, offset, color in FIELDS:
        w = UNIT * n - 0.6
        d.box(x, CELL_Y, w, CELL_H, P[color])
        d.ax.text(x + w / 2, CELL_Y + CELL_H / 2, hexs, fontsize=15, color=P["text"],
                  ha="center", va="center", family="monospace", fontweight="bold", zorder=5)
        d.text(x + w / 2, CELL_Y + CELL_H + 1.9, name, size=9.5, weight="bold")
        d.text(x + w / 2, CELL_Y - 3.3, value, size=8.6, color=P["dim"])
        d.text(x + w / 2, 1.6, f"오프셋 {offset}", size=8, color=P["dim"])
        x += UNIT * n

    head_end = X0 + UNIT * 3 - 0.6
    d.ax.plot([X0, head_end], [CELL_Y + CELL_H + 4.4] * 2, color=P["accent"], lw=1.4)
    d.text((X0 + head_end) / 2, CELL_Y + CELL_H + 5.9, "모든 레코드에 공통인 머리", size=8.8,
           color=P["accent"])
    attr_end = X0 + UNIT * 8 - 0.6
    d.ax.plot([X0 + UNIT * 3, attr_end], [CELL_Y + CELL_H + 4.4] * 2, color=P["orange"], lw=1.4)
    d.text((X0 + UNIT * 3 + attr_end) / 2, CELL_Y + CELL_H + 5.9,
           "Font Attributes 타입이 정한 속성 순서", size=8.8, color=P["orange"])


diagram("32-font-record-bytes", draw, w=14, h=3.7, xmax=100, ymax=26.4)

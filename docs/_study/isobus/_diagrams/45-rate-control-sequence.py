"""CH45 §8 GPS 기반 살포량 제어 순서: GNSS, 처방 맵, TC, 클라이언트, 밸브 (light/dark PNG)."""
from _common import diagram

X = {"gnss": 12, "map": 38, "tc": 66, "cl": 100, "valve": 128}
NAMES = {"gnss": "GNSS 수신기", "map": "처방 맵", "tc": "TC",
         "cl": "클라이언트\n(살포기 ECU)", "valve": "밸브/펌프"}
TOP = 88
ROW = 5.4

# (종류, 보낸 쪽, 받는 쪽, 라벨). 종류 "req"는 실선, "rsp"는 점선, "note"는 생명선 위 메모
ROWS = [
    ("req", "gnss", "tc", "GNSS Position Data (PGN 129029)\n위도 37.123, 경도 127.456"),
    ("req", "tc", "map", "현재 위치 조회"),
    ("rsp", "map", "tc", "구역 A → 목표 200 L/ha"),
    ("req", "tc", "cl", "Value Command\n[DDI=1, Element=3, Value=200]"),
    ("req", "cl", "valve", "밸브 개도량 조절\n(200 L/ha에 맞게)"),
    ("rsp", "valve", "cl", "유량 센서 피드백\n(실제 198 L/ha)"),
    ("rsp", "cl", "tc", "Process Data Value\n[DDI=2, Element=3, Value=198]"),
    ("note", "tc", None, "오차 200 - 198 = 2 L/ha\n허용 범위 안 → 정상"),
    ("req", "gnss", "tc", "GNSS Position Data (PGN 129029)\n위치 변경: 구역 B 진입"),
    ("req", "tc", "map", "현재 위치 조회"),
    ("rsp", "map", "tc", "구역 B → 목표 150 L/ha"),
    ("req", "tc", "cl", "Value Command\n[DDI=1, Element=3, Value=150]"),
    ("req", "cl", "valve", "밸브 개도량 감소"),
    ("rsp", "cl", "tc", "Process Data Value\n[DDI=2, Element=3, Value=151]"),
]


def label(d, x, y, s, size=8.2):
    d.ax.text(x, y, s, fontsize=size, color=d.P["text"], ha="center", va="center", zorder=6,
              linespacing=1.15,
              bbox=dict(boxstyle="square,pad=0.12", facecolor=d.P["bg"], edgecolor="none"))


def draw(d):
    P = d.P
    first = TOP - 10.5
    bottom = first - len(ROWS) * ROW + 1.0
    for key, x in X.items():
        d.box(x - 11, TOP - 7.4, 22, 6.2, P["blue"])
        d.text(x, TOP - 4.3, NAMES[key], size=9.5)
        gaps = [first - i * ROW for i, row in enumerate(ROWS) if row[0] == "note" and row[1] == key]
        start = TOP - 7.6
        for g in gaps:
            d.arrow(x, start, x, g + 2.4, color=P["edge"], lw=1.0, style="-", ls="--")
            start = g - 2.4
        d.arrow(x, start, x, bottom, color=P["edge"], lw=1.0, style="-", ls="--")

    for i, (kind, a, b, text) in enumerate(ROWS):
        y = first - i * ROW
        if kind == "note":
            d.box(X[a] - 13, y - 2.3, 26, 4.6, P["green"], lw=1.0)
            d.text(X[a], y, text, size=8.2)
            continue
        ay = y - 1.6
        color = P["accent"] if kind == "req" else P["orange"]
        ls = "-" if kind == "req" else "--"
        d.arrow(X[a], ay, X[b], ay, color=color, ls=ls, lw=1.6)
        lines = text.count("\n") + 1
        label(d, (X[a] + X[b]) / 2, ay + 1.0 + 1.1 * lines, text)


diagram("45-rate-control-sequence", draw, w=14, h=8.8, xmax=140, ymax=88)

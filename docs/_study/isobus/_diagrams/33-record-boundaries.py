"""CH33 §1 길이 필드 없는 레코드에서 경계 찾기 (light/dark PNG)."""
from _common import diagram

SCALE = 1.0
X0 = 4
STRIP_Y, STRIP_H = 18, 8

# (이름, 바이트 수, Type, 길이 식, 색 키)
RECORDS = [
    ("Container 20", 22, 3, "10 + 6×2 + 2×0 = 22", "gray"),
    ("Soft Key\nMask 40", 10, 4, "6 + 2×2 + 2×0 = 10", "purple"),
    ("Key 41", 15, 5, "7 + 6×1 + 2×1 = 15", "purple"),
    ("Button 50", 19, 6, "13 + 6×1 + 2×0 = 19", "purple"),
]


def draw(d):
    P = d.P
    x = X0
    offset = 0
    starts = []
    for name, size, rtype, formula, color in RECORDS:
        w = size * SCALE
        d.box(x, STRIP_Y, w - 0.4, STRIP_H, P[color])
        d.text(x + w / 2, STRIP_Y + STRIP_H / 2 + 1.0, name, size=8.8, weight="bold")
        d.text(x + w / 2, STRIP_Y + 1.4, f"{size}바이트", size=7.8, color=P["dim"])
        d.text(x, STRIP_Y + STRIP_H + 1.6, f"{offset}", size=8.2, color=P["accent"], ha="left")
        d.text(x + 1.2, STRIP_Y - 2.2, f"Type {rtype}", size=7.8, color=P["orange"], ha="left")
        starts.append((x, offset, formula))
        x += w
        offset += size

    d.text(x, STRIP_Y + STRIP_H + 1.6, f"{offset}", size=8.2, color=P["accent"], ha="left")
    d.text(X0 - 1.5, STRIP_Y + STRIP_H + 1.6, "오프셋", size=8.2, color=P["accent"], ha="right")

    d.box(x, STRIP_Y, 6, STRIP_H, P["chip"])
    d.text(x + 3, STRIP_Y + STRIP_H / 2, "...", size=10)
    unk_x = x + 6.4
    d.box(unk_x, STRIP_Y, 13, STRIP_H, P["bg"], ec=P["orange"], lw=1.4)
    d.text(unk_x + 6.5, STRIP_Y + STRIP_H / 2 + 1.0, "Type ?", size=9, weight="bold",
           color=P["orange"])
    d.text(unk_x + 6.5, STRIP_Y + 1.4, "규칙 모름", size=7.8, color=P["orange"])

    for i, (sx, _, formula) in enumerate(starts):
        nx = starts[i + 1][0] if i + 1 < len(starts) else sx + RECORDS[i][1] * SCALE
        d.arrow(sx + 0.6, STRIP_Y - 4.0, nx + 0.4, STRIP_Y - 4.0, color=P["accent"], lw=1.3,
                rad=0.35)
        depth = 0.35 * (nx - sx) / 2
        d.text((sx + nx) / 2, STRIP_Y - 4.0 - depth - 2.2, formula, size=8.2, color=P["dim"])

    d.text(unk_x + 6.5, STRIP_Y - 6.0, "길이를 셀 수 없다\n뒤 경계를 모두 잃는다", size=8.2,
           color=P["orange"])


diagram("33-record-boundaries", draw, w=14, h=4.62, xmax=100, ymax=33)

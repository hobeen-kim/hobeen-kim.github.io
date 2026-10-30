"""CH16 §7 오브젝트 레코드 공통 구조 — 머리·고정 속성·개수·자식 목록·매크로 목록 (light/dark PNG)."""
from _common import diagram

ROW1 = [
    ("Object ID", "2B, LE", "blue", 9, "Byte 1-2"),
    ("Type", "1B", "blue", 6, "Byte 3"),
    ("고정 속성", "AID 1, 2, ...", "green", 19, "Byte 4..."),
    ("Number of\nobjects", "1B", "brown", 9, ""),
    ("Number of\nmacros", "1B", "brown", 9, ""),
    ("자식 목록", "6B x n", "purple", 17, ""),
    ("매크로 목록", "2B x m", "gray", 17, ""),
]


def cells(d, x, y, items, w, h, gap=0.6, size=9):
    P = d.P
    for label, sub, color in items:
        d.box(x, y, w, h, P[color])
        if sub:
            d.text(x + w / 2, y + h / 2 + 1.0, label, size=size, weight="bold")
            d.text(x + w / 2, y + h / 2 - 1.2, sub, size=7.5, color=P["dim"])
        else:
            d.text(x + w / 2, y + h / 2, label, size=size, weight="bold")
        x += w + gap
    return x - gap


def draw(d):
    P = d.P
    y1, h1 = 34, 7
    x = 3
    spans = {}
    for label, sub, color, w, byte in ROW1:
        d.box(x, y1, w, h1, P[color])
        d.text(x + w / 2, y1 + h1 / 2 + 1.1, label, size=9, weight="bold")
        d.text(x + w / 2, y1 + h1 / 2 - 1.6, sub, size=7.5, color=P["dim"])
        if byte:
            d.text(x + w / 2, y1 + h1 + 1.4, byte, size=8, color=P["dim"])
        spans[label] = (x, x + w)
        x += w + 0.6

    # 자식 목록 한 칸 펼치기
    cx0, cx1 = spans["자식 목록"]
    y2, h2 = 18, 6
    ex0 = 26
    ex1 = cells(d, ex0, y2, [("Object ID", "2B", "purple"), ("X", "2B, signed", "purple"),
                             ("Y", "2B, signed", "purple")], 11, h2)
    d.arrow(cx0, y1, ex0, y2 + h2, color=P["dim"], lw=1.1, style="-", ls="--")
    d.arrow(cx1, y1, ex1, y2 + h2, color=P["dim"], lw=1.1, style="-", ls="--")
    d.text((ex0 + ex1) / 2, y2 - 1.8, "부모 좌상단 기준 상대 위치", size=8, color=P["dim"])

    # 위치 없는 참조 목록(대안 형태)
    y3, h3 = 4, 6
    rx1 = cells(d, 3, y3, [("Object ID", "2B", "chip"), ("Object ID", "2B", "chip"),
                           ("...", "", "chip")], 8, h3, size=8.5)
    d.text(rx1 + 1.2, y3 + h3 / 2, "위치 없는 참조 목록\n(Soft Key Mask, Key Group, Input List)",
           size=8, color=P["dim"], ha="left")

    # 매크로 참조 펼치기: 8비트 / 16비트(v5+)
    mx0, mx1 = spans["매크로 목록"]
    m8x0 = 73
    m8x1 = cells(d, m8x0, y2, [("Event ID", "1B", "gray"), ("Macro ID", "1B", "gray")], 11.5, h2)
    d.arrow(mx0, y1, m8x0, y2 + h2, color=P["dim"], lw=1.1, style="-", ls="--")
    d.arrow(mx1, y1, m8x1, y2 + h2, color=P["dim"], lw=1.1, style="-", ls="--")
    d.text((m8x0 + m8x1) / 2, y2 - 1.8, "8비트 참조", size=8, color=P["dim"])

    m16x0 = 56
    m16x1 = cells(d, m16x0, y3, [("0xFF", "1B", "brown"), ("Macro ID 하위", "1B", "gray"),
                                 ("Event ID", "1B", "gray"), ("Macro ID 상위", "1B", "gray")],
                  9.6, h3, size=8)
    d.text((m8x0 + m8x1) / 2, (y2 - 1.8 + y3 + h3 + 1.6) / 2, "또는", size=8, color=P["dim"])
    d.text((m16x0 + m16x1) / 2, y3 + h3 + 1.6, "16비트 참조(v5+, 개수 2로 셈)", size=8,
           color=P["orange"])


diagram("16-record-anatomy", draw, w=14, h=6.2, xmax=100, ymax=44)

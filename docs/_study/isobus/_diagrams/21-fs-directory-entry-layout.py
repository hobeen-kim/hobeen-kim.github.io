"""52장 5절 Read Directory Response와 Directory Entry 바이트 배치: ISO 11783-13 C.3.5.4, B.21, B.24, B.25 (light/dark PNG)."""
from _common import diagram


def cells(d, x0, y, h, spec, gap=0.5):
    """spec: [(width, top label, value, sub, color)] -> 각 칸의 (x시작, x끝) 목록."""
    P = d.P
    spans = []
    x = x0
    for w, top, val, sub, color in spec:
        d.box(x, y, w, h, P[color])
        d.text(x + w / 2, y + h + 1.3, top, size=8.5, weight="bold")
        if sub:
            d.text(x + w / 2, y + h / 2 + 0.9, val, size=9.5, weight="bold")
            d.text(x + w / 2, y + h / 2 - 1.1, sub, size=7.8, color=P["dim"])
        else:
            d.text(x + w / 2, y + h / 2, val, size=9.5, weight="bold")
        spans.append((x, x + w))
        x += w + gap
    return spans


def draw(d):
    P = d.P

    # 1단: Read Directory Response
    head = [
        (9, "Byte 1", "0x22", "Read File", "blue"),
        (9, "Byte 2", "TAN", "", "gray"),
        (9, "Byte 3", "Error Code", "", "gray"),
        (13, "Byte 4, 5", "Count", "엔트리 수", "green"),
        (53, "Byte 6 ~", "Directory Entry x Count", "가변 길이, 엔트리가 이어 붙는다", "brown"),
    ]
    s1 = cells(d, 3, 47, 6, head)

    # 2단: Directory Entry 1개 (B.21)
    entry = [
        (11, "Byte 1", "Filename\nLength", "", "green"),
        (20, "Byte 2 ~ n", "Filename", "Length 바이트", "brown"),
        (11, "Byte n+1", "Attributes", "속성 비트 8개", "gray"),
        (13, "Byte n+2, n+3", "File Date", "LSB 먼저", "purple"),
        (13, "Byte n+4, n+5", "File Time", "LSB 먼저", "purple"),
        (23, "Byte n+6 ~ n+9", "Size", "uint32, LSB 먼저", "blue"),
    ]
    s2 = cells(d, 3, 27, 6, entry)

    # 1단 엔트리 칸 -> 2단 전체로 펼침
    ex0, ex1 = s1[4]
    d.arrow(ex0 + 2, 46.6, s2[0][0] + 1, 36.4, color=P["dim"], lw=1.0, style="-", ls="--")
    d.arrow(ex1 - 2, 46.6, s2[5][1] - 1, 36.4, color=P["dim"], lw=1.0, style="-", ls="--")

    # 3단: File Date / File Time 비트 그룹
    unit = 2.15
    date = [(7, "15 ~ 9", "Year - 1980"), (4, "8 ~ 5", "Month"), (5, "4 ~ 0", "Day")]
    time_ = [(5, "15 ~ 11", "Hour"), (6, "10 ~ 5", "Minute"), (5, "4 ~ 0", "Second / 2")]

    def bitbar(x0, parts, color):
        x = x0
        for bits, rng, name in parts:
            w = bits * unit
            d.box(x, 6, w, 6, P[color])
            d.text(x + w / 2, 9.9, name, size=8.6, weight="bold")
            d.text(x + w / 2, 7.5, f"bit {rng}", size=7.6, color=P["dim"])
            x += w
        return x

    date_x0 = 3
    date_x1 = bitbar(date_x0, date, "purple")
    time_x0 = 55
    time_x1 = bitbar(time_x0, time_, "purple")
    d.text((date_x0 + date_x1) / 2, 14.2, "File Date: 날짜 2바이트", size=8.8, color=P["dim"])
    d.text((time_x0 + time_x1) / 2, 14.2, "File Time: 시각 2바이트", size=8.8, color=P["dim"])

    dx0, dx1 = s2[3]
    tx0, tx1 = s2[4]
    d.arrow((dx0 + dx1) / 2, 26.6, (date_x0 + date_x1) / 2, 15.6, color=P["dim"], lw=1.0, style="-", ls="--")
    d.arrow((tx0 + tx1) / 2, 26.6, (time_x0 + time_x1) / 2, 15.6, color=P["dim"], lw=1.0, style="-", ls="--")


diagram("21-fs-directory-entry-layout", draw, w=12, h=6.4, xmax=100, ymax=57)

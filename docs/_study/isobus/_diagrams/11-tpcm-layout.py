"""CH11 §4 TP.CM 메시지(8 byte) 바이트 레이아웃 (light/dark PNG)."""
from _common import diagram

CODES = [
    ("0x20", "BAM"),
    ("0x10", "RTS"),
    ("0x11", "CTS"),
    ("0x13", "EndOfMsg"),
    ("0xFF", "Abort"),
]


def draw(d):
    P = d.P
    n = 8
    x0, gap = 2, 0.4
    w = 3.2
    y, h = 8, 5

    x = x0
    for i in range(n):
        color = P["blue"] if i == 0 else P["gray"]
        d.box(x, y, w, h, color)
        d.text(x + w / 2, y + h + 1.2, f"Byte {i + 1}", size=9.5, weight="bold")
        if i == 0:
            d.text(x + w / 2, y + h / 2, "Control\nByte", size=9.5)
        x += w + gap
    x_end = x - gap

    # Byte 2~8 구간 표시 (묶음 괄호 + 설명)
    x2 = x0 + (w + gap)  # byte2 시작
    bracket_y = y - 1.2
    d.arrow(x2, bracket_y, x_end, bracket_y, color=P["dim"], lw=1.2, style="-")
    d.arrow(x2, bracket_y, x2, bracket_y + 0.6, color=P["dim"], lw=1.2, style="-")
    d.arrow(x_end, bracket_y, x_end, bracket_y + 0.6, color=P["dim"], lw=1.2, style="-")
    d.text((x2 + x_end) / 2, bracket_y - 1.4, "메시지 종류에 따라 해석 방식이 다름", size=9, color=P["dim"])

    # Control Byte 값 범례
    legend_y = 2.4
    seg = (x_end - x0) / len(CODES)
    for i, (code, name) in enumerate(CODES):
        cx = x0 + seg * i + seg / 2
        d.text(cx, legend_y, code, size=9.5, weight="bold", color=P["accent"])
        d.text(cx, legend_y - 1.4, name, size=8.5, color=P["dim"])


diagram("11-tpcm-layout", draw, w=12, h=6, xmax=32, ymax=16)

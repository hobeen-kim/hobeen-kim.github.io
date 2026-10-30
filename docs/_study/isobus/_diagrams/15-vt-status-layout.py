"""CH15 §12 VT Status 메시지(8 byte)와 Byte 7 busy 비트 배치 (light/dark PNG)."""
from _common import diagram

BYTES = [
    ("Byte 1", "0xFE", "VT function", "blue"),
    ("Byte 2", "SA", "소유 WS Master", "green"),
    ("Byte 3", "LSB", "", "brown"),
    ("Byte 4", "MSB", "", "brown"),
    ("Byte 5", "LSB", "", "purple"),
    ("Byte 6", "MSB", "", "purple"),
    ("Byte 7", "busy", "비트 8개", "gray"),
    ("Byte 8", "코드", "실행 중 function", "chip"),
]

BITS = [
    ("bit 7", "메모리\n부족", "gray"),
    ("bit 6 (v3+)", "AUX\nlearn 모드", "purple"),
    ("bit 5", "예약\n(0)", "chip"),
    ("bit 4 (v3+)", "풀\n파싱 중", "gray"),
    ("bit 3", "매크로\n실행 중", "green"),
    ("bit 2", "명령\n실행 중", "green"),
    ("bit 1", "NVM\n저장 중", "gray"),
    ("bit 0", "마스크\n갱신 중", "gray"),
]


def bracket(d, x1, x2, y, label):
    P = d.P
    d.arrow(x1, y, x2, y, color=P["dim"], lw=1.2, style="-")
    d.arrow(x1, y, x1, y - 0.7, color=P["dim"], lw=1.2, style="-")
    d.arrow(x2, y, x2, y - 0.7, color=P["dim"], lw=1.2, style="-")
    d.text((x1 + x2) / 2, y + 1.5, label, size=8.5, color=P["dim"])


def draw(d):
    P = d.P
    x0, w, gap = 4.5, 10.5, 1.0
    by, bh = 27, 7.5
    xs = [x0 + i * (w + gap) for i in range(8)]

    for x, (name, val, sub, color) in zip(xs, BYTES):
        ec = P["accent"] if name == "Byte 7" else None
        d.box(x, by, w, bh, P[color], ec=ec)
        d.text(x + w / 2, by + bh + 1.6, name, size=9, weight="bold")
        if sub:
            d.text(x + w / 2, by + bh / 2 + 1.2, val, size=9.5, weight="bold")
            d.text(x + w / 2, by + bh / 2 - 1.3, sub, size=7.5, color=P["dim"])
        else:
            d.text(x + w / 2, by + bh / 2, val, size=9.5, weight="bold")

    bracket(d, xs[2], xs[3] + w, 40.2, "Data/Alarm Mask ID (16bit, LE)")
    bracket(d, xs[4], xs[5] + w, 40.2, "Soft Key Mask ID (16bit, LE)")

    ty, th = 8, 7.5
    d.arrow(xs[6], by, xs[0], ty + th, color=P["dim"], lw=1.1, style="-", ls="--")
    d.arrow(xs[6] + w, by, xs[7] + w, ty + th, color=P["dim"], lw=1.1, style="-", ls="--")

    for x, (name, label, color) in zip(xs, BITS):
        d.box(x, ty, w, th, P[color])
        d.text(x + w / 2, ty + th / 2, label, size=8.5)
        d.text(x + w / 2, ty - 1.6, name, size=8, color=P["dim"])

    d.text(xs[1] + w / 2, 2.6, "바뀌면 즉시 송신", size=8, color=P["violet"])
    d.text((xs[4] + xs[5] + w) / 2, 2.6, "1이면 Byte 8 유효", size=8, color=P["accent"])


diagram("15-vt-status-layout", draw, w=12, h=5.6, xmax=100, ymax=44)

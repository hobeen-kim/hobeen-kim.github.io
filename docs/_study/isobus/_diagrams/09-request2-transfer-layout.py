"""CH09 §10 Request2(8 byte)와 Transfer(가변 길이) 데이터 배치 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ---------- Request2 ----------
    x0, cw, gap = 14, 9.6, 0.5
    bx = lambda i: x0 + (i - 1) * (cw + gap)
    y, h = 36, 6
    d.text(2, y + h / 2, "Request2", size=10, weight="bold", ha="left")
    for i in range(1, 9):
        d.text(bx(i) + cw / 2, y + h + 1.8, f"Byte {i}", size=8.6, weight="bold")
    d.box(bx(1), y, bx(3) + cw - bx(1), h, P["purple"])
    d.text((bx(1) + bx(3) + cw) / 2, y + h / 2, "요청 PGN (LSB 먼저)", size=8.8)
    d.box(bx(4), y, cw, h, P["brown"])
    d.text(bx(4) + cw / 2, y + h / 2, "특수 지시", size=8.6)
    d.box(bx(5), y, bx(7) + cw - bx(5), h, P["green"])
    d.text((bx(5) + bx(7) + cw) / 2, y + h / 2, "확장 식별자 (LSB 먼저)", size=8.8)
    d.box(bx(8), y, cw, h, P["gray"])
    d.text(bx(8) + cw / 2, y + h / 2, "예약", size=8.6)

    # Byte 4 비트 확대: bit 8~6 예약, bit 5~3 확장 ID 종류, bit 2~1 Transfer 사용
    bits_y, bh, bw, bstart = 24, 4.8, 6.6, 26
    for k in range(8):
        d.text(bstart + k * bw + bw / 2, bits_y + bh + 1.5, f"bit {8 - k}", size=8, color=P["dim"])
    groups = [(0, 3, "예약", "gray"), (3, 3, "확장 ID 종류\n000~011, 111", "green"),
              (6, 2, "Transfer 사용\n00 No / 01 Yes", "blue")]
    for start, n, label, c in groups:
        d.box(bstart + start * bw, bits_y, n * bw - 0.4, bh, P[c])
        d.text(bstart + start * bw + (n * bw - 0.4) / 2, bits_y + bh / 2, label, size=8.3)
    d.arrow(bx(4) + cw / 2, y, bstart + 4 * bw, bits_y + bh + 3.0, color=P["dim"], lw=1.2)

    # ---------- Transfer ----------
    ty, th = 6, 6
    d.text(2, ty + th / 2, "Transfer", size=10, weight="bold", ha="left")
    segs = [
        ("a  요청 PGN\n(3 byte)", 15, "purple"),
        ("b  길이\n= 5 + len(d)", 10, "brown"),
        ("c  CF 신원\n(NAME 바이트 5~8)", 15, "blue"),
        ("d  그 CF의 PGN 데이터\n(가변)", 17, "green"),
        ("b", 4.5, "brown"),
        ("c", 7, "blue"),
        ("d", 9, "green"),
        ("...", 6, "gray"),
    ]
    x = 14
    for label, w, c in segs:
        d.box(x, ty, w - 0.4, th, P[c])
        d.text(x + (w - 0.4) / 2, ty + th / 2, label, size=8.4)
        x += w
    s0 = 14 + 15
    s1 = s0 + 10 + 15 + 17 - 0.4
    d.ax.plot([s0, s1], [ty + th + 1.8, ty + th + 1.8], color=P["accent"], lw=1.2)
    for xx in (s0, s1):
        d.ax.plot([xx, xx], [ty + th + 1.0, ty + th + 1.8], color=P["accent"], lw=1.2)
    d.text((s0 + s1) / 2, ty + th + 3.3, "첫 데이터 세트 (59904 응답과 같은 내용)", size=8.4, color=P["accent"])
    d.text(s1 + 0.4 + 13, ty + th + 3.3, "둘째 이후 세트", size=8.4, color=P["dim"])


diagram("09-request2-transfer-layout", draw, w=12.5, h=4.9, xmax=100, ymax=45)

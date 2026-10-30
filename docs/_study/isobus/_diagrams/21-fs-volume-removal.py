"""CH21 §4.4 이동식 볼륨 제거 절차 — ISO 11783-13 C.1.6~C.1.7, B.30~B.32 (light/dark PNG)."""
from _common import diagram

A, FS, B = 12, 50, 88

# (from, to, label, response?, broadcast?)
ROWS = [
    (FS, None, "Volume Status Response: Present (매체 감지)", True, True),
    (A, FS, "Volume Status Request: Mode 0x02 (제거 준비 요청)", False, False),
    (FS, None, "Volume Status Response: Preparing for removal", True, True),
    (B, FS, "Volume Status Request: Mode 0x01 (사용 중, Maintain)", False, False),
    (B, FS, "Close File 0x24 (열린 파일 정리)", False, False),
    (FS, B, "Close File Response 0x24", True, False),
    (B, FS, "Volume Status Request: Mode 0x00 (사용 안 함)", False, False),
    (FS, None, "Volume Status Response: Removed", True, True),
]

Y0, STEP = 47.0, 5.4


def draw(d):
    P = d.P
    for x, name in ((A, "Client A\n(제거 요청)"), (FS, "File Server"), (B, "Client B\n(파일 사용 중)")):
        d.box(x - 9, 52, 18, 6, P["blue"] if name == "File Server" else P["chip"])
        d.text(x, 55, name, size=9.5, weight="bold")
        d.arrow(x, 51.8, x, 2, color=P["edge"], lw=1.0, style="-", ls="--")

    for i, (a, b, label, resp, glob) in enumerate(ROWS):
        y = Y0 - i * STEP
        ls = "--" if resp else "-"
        if glob:
            d.arrow(FS, y, A + 0.4, y, lw=1.4, ls=ls, color=P["orange"])
            d.arrow(FS, y, B - 0.4, y, lw=1.4, ls=ls, color=P["orange"])
            d.text((A + FS) / 2, y + 1.3, label, size=8.4)
            d.text((FS + B) / 2, y + 1.3, "전역 DA 0xFF", size=8, color=P["orange"])
        else:
            d.arrow(a, y, b, y, lw=1.4, ls=ls)
            d.text((a + b) / 2, y + 1.3, label, size=8.4)

    # Maintain 반복 구간 표시
    y_top, y_bot = Y0 - 3 * STEP + 2.4, Y0 - 6 * STEP - 1.0
    d.arrow(95.5, y_top, 95.5, y_bot, color=P["violet"], lw=1.2, style="-")
    d.arrow(94.5, y_top, 95.5, y_top, color=P["violet"], lw=1.2, style="-")
    d.arrow(94.5, y_bot, 95.5, y_bot, color=P["violet"], lw=1.2, style="-")
    d.text(97, (y_top + y_bot) / 2, "마지막 Maintain\n후 2 s 유지\n(최대 Max Time)", size=7.8,
           color=P["violet"], ha="left")


diagram("21-fs-volume-removal", draw, w=12.5, h=6.4, xmax=106, ymax=59)

"""CH9 §5 데이터 필드(8byte) 내 SPN 배치 (light/dark PNG)."""
from _common import diagram

# (SPN 라벨, byte[i]=값, 결과, 색상 키)
BYTES = [
    ("SPN 110", "byte[0]=0xB0", "→ 136°C", "blue"),
    ("SPN 174", "byte[1]=0x32", "→ 10°C", "green"),
    ("SPN 175", "byte[2]=0x04", "(LSB)", "brown"),
    ("SPN 175", "byte[3]=0xFF", "(MSB)", "brown"),
    ("SPN 176", "byte[4]=0xFF", "(N/A)", "gray"),
    ("SPN 176", "byte[5]=0xFF", "(N/A)", "gray"),
    ("SPN 1134", "byte[6]=0xFF", "(N/A)", "purple"),
    ("SPN 1135", "byte[7]=0xFF", "(N/A)", "orange"),
]


def draw(d):
    P = d.P
    n = len(BYTES)
    x0, gap = 2, 0.5
    w = 10.5
    y, h = 8, 9

    x = x0
    for name, val, result, color in BYTES:
        d.box(x, y, w, h, P[color])
        in_box_color = P["bg"] if color in ("orange", "accent") else None
        d.text(x + w / 2, y + h * 0.68, name, size=8.3, weight="bold", color=in_box_color)
        d.text(x + w / 2, y + h * 0.4, val, size=7.3, color=in_box_color)
        d.text(x + w / 2, y - 1.8, result, size=7.6, color=P["dim"])
        x += w + gap


diagram("09-spn-byte-layout", draw, w=14, h=4.6, xmax=97, ymax=24)

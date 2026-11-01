"""CH12 NAME 0xA00882000D27A120을 8바이트, 64비트, 필드 순으로 풀어 읽기 (light/dark PNG)."""
from matplotlib.patches import Patch

from _common import diagram

NAME = 0xA00882000D27A120
BYTES_BYTE8_FIRST = NAME.to_bytes(8, "big")
BITS_MSB_FIRST = format(NAME, "064b")
FIELDS = [
    ("AAC", 1, "addr"), ("IG", 3, "what"), ("DCI", 4, "nth"), ("DC", 7, "what"),
    ("R", 1, "rsvd"), ("Function", 8, "what"), ("FI", 5, "nth"), ("EI", 3, "nth"),
    ("MC", 11, "who"), ("Identity number", 21, "who"),
]
GROUP_COLOR = {"addr": "purple", "what": "blue", "nth": "green", "who": "brown", "rsvd": "gray"}
GROUP_LABEL = [("addr", "주소를 옮길 수 있나"), ("what", "무슨 장치인가"),
               ("nth", "몇 번째인가"), ("who", "누가 만들었나"), ("rsvd", "예약")]


def field_values():
    values, shift = {}, 64
    for label, n_bits, _ in FIELDS:
        shift -= n_bits
        values[label] = (NAME >> shift) & ((1 << n_bits) - 1)
    return values


def draw(d):
    P = d.P
    x0, cw = 6, 2.0
    byte_y, byte_h = 33, 6.0
    bit_y, bit_h = 17, 6.5

    for i, b in enumerate(BYTES_BYTE8_FIRST):
        bx = x0 + i * 8 * cw
        d.box(bx + 0.3, byte_y, 8 * cw - 0.6, byte_h, P["chip"])
        d.text(bx + 8 * cw / 2, byte_y + byte_h / 2, f"{b:02X}", size=12, weight="bold")
        d.text(bx + 8 * cw / 2, byte_y + byte_h + 1.8, f"Byte {8 - i}", size=8.2,
               color=P["dim"])
    for k in range(9):
        ex = x0 + k * 8 * cw
        d.ax.plot([ex, ex], [byte_y - 0.2, bit_y + bit_h + 0.6], color=P["edge"],
                  lw=0.8, ls=(0, (2, 2)), zorder=1)

    pos = 0
    spans = []
    for label, n_bits, group in FIELDS:
        for j in range(n_bits):
            i = pos + j
            d.box(x0 + i * cw + 0.08, bit_y, cw - 0.16, bit_h, P[GROUP_COLOR[group]],
                  lw=0.7, r=0.004)
            d.text(x0 + i * cw + cw / 2, bit_y + bit_h / 2, BITS_MSB_FIRST[i], size=8.2)
        spans.append((pos, pos + n_bits, label))
        pos += n_bits

    for start, _, _ in spans[1:]:
        xx = x0 + start * cw
        d.ax.plot([xx, xx], [bit_y - 0.8, bit_y + bit_h + 0.8], color=P["text"],
                  lw=1.6, zorder=6)

    values = field_values()
    for start, end, label in spans:
        xa, xb = x0 + start * cw + 0.25, x0 + end * cw - 0.25
        d.ax.plot([xa, xa, xb, xb], [bit_y - 1.2, bit_y - 2.0, bit_y - 2.0, bit_y - 1.2],
                  color=P["accent"], lw=1.2, zorder=3)
        cx = (xa + xb) / 2
        d.text(cx, bit_y - 4.4, label, size=8.4, color=P["dim"])
        d.text(cx, bit_y - 7.8, str(values[label]), size=9.6, weight="bold",
               color=P["accent"])

    handles = [Patch(facecolor=P[GROUP_COLOR[g]], edgecolor=P["edge"], label=t)
               for g, t in GROUP_LABEL]
    d.ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.03, 0.0), ncol=5,
                fontsize=8.5, frameon=False, labelcolor=P["dim"])


diagram("12-name-decode", draw, w=14, h=4.3, xmax=140, ymax=43)

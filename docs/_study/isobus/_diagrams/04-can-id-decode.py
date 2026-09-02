"""CH4 §7 CAN ID 0x0CF004FE(29bit Extended) 바이트→비트 분해 (light/dark PNG).

검산 (Priority3 + EDP1 + DP1 + PF8 + PS8 + SA8 = 29bit, 상위 3bit는 32bit 16진 표기의 미사용 패딩):
  0x0CF004FE = 0000 1100  1111 0000  0000 0100  1111 1110
  Byte0(0x0C) = pad(000) + Priority(011=3) + EDP(0) + DP(0)
  Byte1(0xF0) = PF
  Byte2(0x04) = PS   → PGN = PF·PS = 0xF004 = 61444 (EEC1)
  Byte3(0xFE) = SA(254)
"""
from _common import diagram

BYTES = ["00001100", "11110000", "00000100", "11111110"]
HEX = ["0x0C", "0xF0", "0x04", "0xFE"]

CW, GAP = 2.35, 2.2
X0 = 3
Y, H = 13, 7


def draw(d):
    P = d.P

    x = X0
    byte_x0 = []
    for byte_bits, hx in zip(BYTES, HEX):
        byte_x0.append(x)
        d.text(x + (CW * 8) / 2, Y + H + 2.0, hx, size=10, weight="bold")
        for j, b in enumerate(byte_bits):
            d.box(x + j * CW, Y, CW * 0.92, H, P["chip"], ec=P["edge"], lw=0.6, r=0.0)
            d.text(x + j * CW + CW * 0.46, Y + H / 2, b, size=8.5)
        x += 8 * CW + GAP

    # Byte0 하위 필드 (pad / Priority / EDP / DP)
    b0 = byte_x0[0]
    sub = [("미사용", 0, 3, "gray"), ("Priority(3)", 3, 3, "blue"),
           ("EDP", 6, 1, "green"), ("DP", 7, 1, "purple")]
    for name, start, n, key in sub:
        sx0, sx1 = b0 + start * CW, b0 + (start + n) * CW - CW * 0.08
        ly = Y - 1.6
        d.ax.plot([sx0, sx1], [ly, ly], color=P["edge"], lw=1.0)
        d.ax.plot([sx0, sx0], [ly, ly + 0.9], color=P["edge"], lw=1.0)
        d.ax.plot([sx1, sx1], [ly, ly + 0.9], color=P["edge"], lw=1.0)
        d.text((sx0 + sx1) / 2, ly - 1.4, name, size=7.6, color=P["dim"])

    # Byte1~3 전체 필드 라벨 (PF / PS / SA)
    labels = ["PF (8bit)", "PS (8bit)", "SA (8bit)"]
    for bx, label in zip(byte_x0[1:], labels):
        sx0, sx1 = bx, bx + 8 * CW - CW * 0.08
        ly = Y - 1.6
        d.ax.plot([sx0, sx1], [ly, ly], color=P["edge"], lw=1.0)
        d.ax.plot([sx0, sx0], [ly, ly + 0.9], color=P["edge"], lw=1.0)
        d.ax.plot([sx1, sx1], [ly, ly + 0.9], color=P["edge"], lw=1.0)
        d.text((sx0 + sx1) / 2, ly - 1.4, label, size=8.2, color=P["dim"])

    # PF+PS = PGN 묶음 표시
    pf_x0, ps_x1 = byte_x0[1], byte_x0[2] + 8 * CW - CW * 0.08
    ly2 = Y - 4.4
    d.ax.plot([pf_x0, ps_x1], [ly2, ly2], color=P["accent"], lw=1.2)
    d.ax.plot([pf_x0, pf_x0], [ly2, ly2 + 0.7], color=P["accent"], lw=1.2)
    d.ax.plot([ps_x1, ps_x1], [ly2, ly2 + 0.7], color=P["accent"], lw=1.2)
    d.text((pf_x0 + ps_x1) / 2, ly2 - 1.5, "PGN = 0xF004 (61444, EEC1)",
           size=8.6, color=P["accent"], weight="bold")


diagram("04-can-id-decode", draw, w=11.5, h=4.4, xmax=88, ymax=27)

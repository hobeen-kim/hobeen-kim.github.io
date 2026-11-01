"""CH14 §12 ISOBUS compliance certification 메시지(PGN 64834) 비트 배치: 3판 형식 (light/dark PNG)."""
from _common import diagram

COLOR = {"Y": "green", "R": "purple", "T": "brown", "L": "blue", "V": "chip", "0": "gray"}
ROW1 = [
    ["R2", "R1", "Y6", "Y5", "Y4", "Y3", "Y2", "Y1"],
    ["L3", "L2", "L1", "R5", "R4", "T2", "T1", "R3"],
    ["L11", "L10", "L9", "L8", "L7", "L6", "L5", "L4"],
]
BYTE6 = ["V", "0", "0", "0", "0", "0", "0", "0"]
CELL = 3.6


def bit_cells(d, x0, y, h, labels, byte_no):
    P = d.P
    d.text(x0 + 4 * CELL, y + h + 3.4, f"Byte {byte_no}", size=10, weight="bold")
    for i, lab in enumerate(labels):
        cx = x0 + i * CELL
        key = lab.rstrip("0123456789") or "0"
        ec = P["accent"] if key == "V" else None
        d.box(cx, y, CELL, h, P[COLOR[key]], ec=ec, lw=2.0 if key == "V" else 1.0, r=0.005)
        d.text(cx + CELL / 2, y + h + 1.2, str(8 - i), size=7.5, color=P["dim"])
        d.text(cx + CELL / 2, y + h / 2, lab, size=8.5, weight="bold")


def whole_byte(d, x, y, w, h, byte_no, top, sub, color):
    P = d.P
    d.box(x, y, w, h, P[color])
    d.text(x + w / 2, y + h + 3.4, f"Byte {byte_no}", size=10, weight="bold")
    d.text(x + w / 2, y + h / 2 + 1.0, top, size=9.5, weight="bold")
    d.text(x + w / 2, y + h / 2 - 1.5, sub, size=7.5, color=P["dim"])


def draw(d):
    P = d.P
    for b, labels in enumerate(ROW1):
        bit_cells(d, 4 + b * (8 * CELL + 2.2), 28, 6, labels, b + 1)

    y2, h2 = 13, 6
    whole_byte(d, 4, y2, 12, h2, 4, "0x00", "Reserved", "gray")
    whole_byte(d, 18, y2, 12, h2, 5, "0x00", "Reserved", "gray")
    bit_cells(d, 32, y2, h2, BYTE6, 6)
    whole_byte(d, 63, y2, 15, h2, 7, "Ref LSB", "Reference number", "chip")
    whole_byte(d, 80, y2, 15, h2, 8, "Ref MSB", "(16 bit, LE)", "chip")

    legend = [("Y", "Y 시험 프로토콜 연도 (6 bit, +2000)"), ("R", "R 개정 번호 (5 bit)"),
              ("T", "T 시험소 종류 (2 bit)"), ("L", "L 시험소 ID (11 bit)"),
              ("V", "V 메시지 개정 (1 = 3판 이후)"), ("0", "0 예약 (0으로 송신)")]
    for i, (key, label) in enumerate(legend):
        lx, ly = 4 + (i % 3) * 32, 6.2 - (i // 3) * 4.2
        ec = P["accent"] if key == "V" else None
        d.box(lx, ly - 1.1, 2.2, 2.2, P[COLOR[key]], ec=ec, lw=1.5 if key == "V" else 1.0, r=0.005)
        d.text(lx + 3.2, ly, label, size=8.5, ha="left")


diagram("14-cert-layout", draw, w=13, h=5.6, xmax=100, ymax=43)

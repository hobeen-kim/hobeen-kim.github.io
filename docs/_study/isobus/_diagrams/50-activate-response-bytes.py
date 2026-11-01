"""50장 3절: Object-pool Activate/Deactivate Response 8바이트 지도와 두 예 (light/dark PNG)."""
from _common import diagram

X0, CW, GAP = 12.5, 10.0, 0.6

# (첫 바이트, 끝 바이트, 색, 필드 라벨)
FIELDS = [
    (1, 1, "gray", "응답 종류"),
    (2, 2, "brown", "오류 비트"),
    (3, 4, "blue", "부모 Object ID"),
    (5, 6, "blue", "오류 Object ID"),
    (7, 7, "brown", "풀 오류 비트"),
    (8, 8, "gray", "예약"),
]
ROWS = [
    ("정상", "91 00 FF FF FF FF 00 FF"),
    ("오류 예", "91 01 03 00 08 00 09 FF"),
]
BIT_LISTS = [
    (2, "Byte 2", ["bit 1  DDOP에 오류 (Byte 3~7 참조)", "bit 2  활성화 중 메모리 부족",
                   "bit 3  기타 오류", "bit 4  같은 structure label의 다른 DDOP (v4)"]),
    (7, "Byte 7", ["bit 1  지원하지 않는 method·attribute", "bit 2  모르는 오브젝트 참조 (누락)",
                   "bit 3  기타 오류", "bit 4  휘발성 메모리에서 삭제함"]),
]


def cx(n):
    return X0 + (n - 1) * (CW + GAP)


def draw(d):
    P = d.P
    for n in range(1, 9):
        d.text(cx(n) + CW / 2, 45.0, f"Byte {n}", size=7.8, color=P["dim"])
    for a, b, color, label in FIELDS:
        x1, x2 = cx(a), cx(b) + CW
        d.box(x1, 37.5, x2 - x1, 5.4, P[color])
        d.text((x1 + x2) / 2, 40.2, label, size=7.6, weight="bold")

    for r, (name, hexs) in enumerate(ROWS):
        y = 29.5 - r * 7.0
        d.text(X0 - 1.2, y + 2.3, name, size=8.0, weight="bold", ha="right")
        for n, v in enumerate(hexs.split(), 1):
            hot = r == 1 and 2 <= n <= 7
            d.box(cx(n), y, CW, 4.6, P["chip"], ec=P["accent"] if hot else P["edge"],
                  lw=1.8 if hot else 1.0)
            d.text(cx(n) + CW / 2, y + 2.3, v, size=9.0, weight="bold",
                   color=P["accent"] if hot else None)

    for k, (byte_no, title, lines) in enumerate(BIT_LISTS):
        bx, bw = (X0, 40.5) if k == 0 else (X0 + 43.6, 40.5)
        d.box(bx, 1.2, bw, 13.6, P["bg"], lw=1.0)
        d.text(bx + 1.2, 12.9, title, size=7.8, weight="bold", ha="left")
        for i, line in enumerate(lines):
            d.text(bx + 1.2, 10.4 - i * 2.4, line, size=7.0, ha="left")
        d.arrow(cx(byte_no) + CW / 2, 22.4, bx + bw / 2, 14.9, color=P["dim"], lw=1.1)


diagram("50-activate-response-bytes", draw, w=12.5, h=6.0, xmax=100, ymax=48)

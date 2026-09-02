"""CH4 §6 실제 비트열 분해 — 스터핑 제거와 필드 경계 (light/dark PNG)."""
from _common import diagram

RX = "0001001000110000011010101011110011011111011100111100" + "1011111111"   # 62비트
DE = "00010010001100000101010101111001101111111100111100" + "1011111111"      # 60비트
STUFFED = {17, 40}

FIELDS = [
    ("SOF", 1, "chip", 0), ("Identifier (11비트)", 11, "blue", 1), ("RTR", 1, "chip", 0),
    ("IDE", 1, "chip", 1), ("r0", 1, "chip", 0), ("DLC", 4, "green", 1),
    ("Data (2바이트)", 16, "brown", 0), ("CRC (15비트)", 15, "purple", 1),
    ("CRC구분", 1, "chip", 0), ("ACK", 1, "accent", 1), ("ACK구분", 1, "chip", 0),
    ("EOF", 7, "gray", 1),
]

CW, X0 = 1.45, 4.0
R1Y, R2Y, BH = 29.0, 12.0, 5.0


def draw(d):
    P = d.P

    # 수신 비트열 (스터핑 포함)
    d.text(X0, R1Y + BH + 4.0, "버스에서 수신한 비트열 (62비트)",
           size=10, ha="left", color=P["dim"])
    for i, b in enumerate(RX):
        s = i in STUFFED
        d.box(X0 + i * CW, R1Y, CW * 0.92, BH,
              P["orange"] if s else P["chip"],
              ec=P["orange"] if s else P["edge"], lw=1.4 if s else 0.6, r=0.0)
        d.text(X0 + i * CW + CW * 0.46, R1Y + BH / 2, b, size=6,
               color=P["bg"] if s else P["text"])
    for i in sorted(STUFFED):
        d.text(X0 + i * CW + CW * 0.46, R1Y - 2.0, "▲", size=6, color=P["orange"])
    d.text(X0 + 42 * CW, R1Y - 4.2, "스터핑 비트 2개 — 데이터가 아니므로 먼저 제거한다",
           size=9, ha="left", color=P["orange"])

    # 제거 후 + 필드 경계
    d.text(X0, R2Y + BH + 8.2, "스터핑 제거 후 필드로 자른다 (60비트)",
           size=10, ha="left", color=P["dim"])
    pos = 0
    for name, n, key, lvl in FIELDS:
        for j in range(n):
            i = pos + j
            d.box(X0 + i * CW, R2Y, CW * 0.92, BH, P[key], ec=P["edge"], lw=0.6, r=0.0)
            d.text(X0 + i * CW + CW * 0.46, R2Y + BH / 2, DE[i], size=6,
                   color=P["bg"] if key == "accent" else P["text"])
        x0, x1 = X0 + pos * CW, X0 + (pos + n) * CW - CW * 0.08
        ly = R2Y + BH + (1.6 if lvl == 0 else 4.6)
        d.ax.plot([x0, x1], [ly, ly], color=P["edge"], lw=1.0)
        d.ax.plot([x0, x0], [ly - 0.9, ly], color=P["edge"], lw=1.0)
        d.ax.plot([x1, x1], [ly - 0.9, ly], color=P["edge"], lw=1.0)
        d.text((x0 + x1) / 2, ly + 1.3, name, size=8.2)
        pos += n

    # 해석 결과
    d.text(X0, 6.4, "ID = 0x123    데이터 프레임(RTR 0)    표준 11비트(IDE 0)    "
                    "DLC 2 → Data 0xAB 0xCD    CRC 0x7F3C",
           size=9.5, ha="left")
    d.text(X0, 3.0, "DLC를 읽기 전에는 프레임 전체 길이를 알 수 없다 — "
                    "데이터 길이가 정해져야 CRC 시작 위치가 정해진다",
           size=9, ha="left", color=P["dim"])


diagram("04-frame-decode", draw, w=14, h=6.2, xmax=100, ymax=45)

"""CH57 §1 GPS 위치 (37.5015, 127.0005)에서 grid type 2 셀 값까지 계산 단계 (light/dark PNG)."""
from _common import diagram

STEPS = [
    # (row, col, title, lines, color key)
    (0, 0, "1  GPS 위치", ["위도 37.5015", "경도 127.0005"], "blue"),
    (0, 1, "2  원점 빼기", ["위도 - A = 37.5015 - 37.500 = 0.0015",
                          "경도 - B = 127.0005 - 127.000 = 0.0005"], "blue"),
    (0, 2, "3  셀 크기로 나누고 내림", ["row = floor(0.0015 ÷ 0.001) = 1",
                                  "col = floor(0.0005 ÷ 0.001) = 0"], "blue"),
    (1, 0, "4  셀 번호", ["index = row × E + col", "= 1 × 2 + 0 = 2"], "green"),
    (1, 1, "5  바이트 위치 (type 2, PDV 1개)", ["offset = index × 4 = 8",
                                          "바이트 8~11을 읽는다"], "green"),
    (1, 2, "6  값 읽기", ["10 27 00 00 → 0x00002710 = 10000",
                        "× 0.01 (VPN) = 100 kg/ha"], "brown"),
]

W, H = 30.0, 15.0
X0 = [2.0, 35.0, 68.0]
Y0 = [24.5, 3.0]


def draw(d):
    P = d.P
    for r, c, title, body, key in STEPS:
        x, y = X0[c], Y0[r]
        d.box(x, y, W, H, P[key])
        d.text(x + 1.4, y + H - 2.6, title, size=9.5, weight="bold", ha="left")
        for i, s in enumerate(body):
            d.text(x + 1.4, y + H - 7.0 - i * 3.4, s, size=8.6, ha="left")
    for c in range(2):
        d.arrow(X0[c] + W, Y0[0] + H / 2, X0[c + 1], Y0[0] + H / 2)
        d.arrow(X0[c] + W, Y0[1] + H / 2, X0[c + 1], Y0[1] + H / 2)
    d.arrow(X0[2] + W / 2, Y0[0], X0[0] + W / 2, Y0[1] + H, rad=0.0)
    d.text(99, 42.4, "A = 37.500, B = 127.000, C = D = 0.001, E = 2", size=8.5,
           ha="right", color=P["dim"])


diagram("57-gps-to-cell-lookup", draw, w=12, h=5.4, xmax=100, ymax=45)

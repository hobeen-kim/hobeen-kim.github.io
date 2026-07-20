"""CH18 §4 배선 — ESP32 TWAI(GPIO 21/22) → CAN 트랜시버 → CAN 버스 커넥터."""
from _common import diagram


def draw(d):
    P = d.P

    # ESP32 보드
    d.box(3, 8, 26, 34, P["blue"])
    d.text(16, 39, "ESP32 (ESP-WROOM-32)", size=11, weight="bold")

    pins = [
        (34, "GPIO 21", "TWAI TX"),
        (29, "GPIO 22", "TWAI RX"),
        (23, "3V3", "전원"),
        (18, "GND", "접지"),
    ]
    for y, pin, role in pins:
        d.box(6, y - 2, 12, 4, P["chip"])
        d.text(12, y, pin, size=9.5)
        d.text(24, y, role, size=8.5, color=P["dim"])

    # 트랜시버
    d.box(40, 12, 22, 26, P["purple"])
    d.text(51, 35, "CAN 트랜시버\n(SN65HVD230 등)", size=10.5, weight="bold")
    for y, label in [(29, "CTX"), (24, "CRX"), (19, "VCC"), (15, "GND")]:
        d.box(42, y - 1.8, 8, 3.6, P["chip"])
        d.text(46, y, label, size=9)
    for y, label in [(29, "CANH"), (24, "CANL")]:
        d.box(52, y - 1.8, 8, 3.6, P["chip"])
        d.text(56, y, label, size=8.5)

    # ESP32 → 트랜시버 배선
    d.arrow(18, 34, 42, 29, color=P["orange"], style="-", lw=1.6, rad=0.05)
    d.arrow(42, 24, 18, 29, color=P["orange"], style="-", lw=1.6, rad=-0.05)
    d.arrow(18, 23, 42, 19, color=P["accent"], style="-", lw=1.6, rad=0.05)
    d.arrow(18, 18, 42, 15, color=P["edge"], style="-", lw=1.6, rad=0.05)

    # 커넥터
    d.box(73, 12, 24, 26, P["brown"])
    d.text(85, 35, "버스 커넥터", size=10.5, weight="bold")
    d.text(85, 32, "Deutsch DT 4핀 /\nISOBUS 진단 커넥터", size=8.8, color=P["dim"])
    for y, label in [(25, "CAN_H"), (20, "CAN_L"), (15, "GND")]:
        d.box(76, y - 1.8, 18, 3.6, P["chip"])
        d.text(85, y, label, size=9)

    d.arrow(60, 29, 76, 25, color=P["violet"], style="-", lw=1.8, rad=0.05)
    d.arrow(60, 24, 76, 20, color=P["violet"], style="-", lw=1.8, rad=0.05)
    d.arrow(50, 15, 76, 15, color=P["edge"], style="-", lw=1.4)

    d.text(34.5, 9, "저전압 로직", size=9, color=P["dim"])
    d.text(67.5, 9, "차동 CAN 신호\n(120Ω 종단)", size=9, color=P["dim"])

    d.text(50, 4, "TWAI 핀에 CAN 버스를 직접 연결하면 안 된다 — 트랜시버 필수",
           size=9.5, color=P["orange"])


diagram("18-esp32-wiring", draw, w=13, h=6.0, ymax=44)

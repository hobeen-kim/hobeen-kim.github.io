"""41장 위치 기반 제어 흐름: GNSS 위치 → TC-Server(처방 맵 조회) → Value Command → TC-Client (light/dark PNG)."""
from _common import diagram

Y, H = 9, 11


def node(d, x, w, title, sub, color, y=Y, h=H):
    d.box(x, y, w, h, d.P[color])
    if sub:
        d.text(x + w / 2, y + h / 2 + 1.8, title, size=10.5, weight="bold")
        d.text(x + w / 2, y + h / 2 - 1.9, sub, size=8.4)
    else:
        d.text(x + w / 2, y + h / 2, title, size=11, weight="bold")


def draw(d):
    P = d.P
    node(d, 1, 19, "GNSS 수신기", "(NMEA 2000 / NMEA 0183)", "gray")
    node(d, 25, 19, "GNSS Position Data", "(PGN 129029)", "chip")
    node(d, 49, 14, "TC-Server", "", "green")
    node(d, 68, 16, "Value Command", "(Setpoint 전달)", "chip")
    node(d, 88.5, 11, "TC-Client", "(작업기 ECU)", "blue")
    node(d, 47.5, 17, "처방 맵", "(Prescription Map)", "brown", y=29, h=9)

    mid = Y + H / 2
    d.arrow(20.2, mid, 24.8, mid)
    d.text(22.5, 6.6, "위치 데이터", size=9, color=P["accent"])
    d.arrow(44.2, mid, 48.8, mid)
    d.arrow(63.2, mid, 67.8, mid)
    d.text(65.5, 6.6, "해당 위치 목표값", size=9, color=P["accent"])
    d.arrow(84.2, mid, 88.3, mid)

    d.arrow(56, 28.8, 56, 20.2)
    d.text(57.5, 24.5, "위치별 목표값 조회", size=9, color=P["accent"], ha="left")


diagram("41-position-control-flow", draw, w=12, h=4.4, xmax=100, ymax=40)

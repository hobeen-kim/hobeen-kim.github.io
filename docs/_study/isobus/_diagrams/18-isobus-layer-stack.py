"""18장 5절: ISOBUS 계층 구조와 J1939의 관계 (light/dark PNG)."""
from _common import diagram

LAYERS = [
    # (y0, 계층 이름, 내용, 색 키)
    (44, "응용 계층\n(Application)",
     "VT  ISO 11783-6       TC  ISO 11783-10\nTECU  ISO 11783-9     진단  ISO 11783-12", "purple"),
    (31, "네트워크 계층\n(Network)",
     "ISO 11783-4 / J1939-31\nNIU (세그먼트 상호연결 장치)", "blue"),
    (18, "데이터 링크 계층\n(Data Link)",
     "ISO 11783-3 / J1939-21\n29비트 CAN ID, PGN 체계, TP·ETP (멀티 패킷 전송)", "blue"),
    (5, "물리 계층\n(Physical)",
     "ISO 11783-2 / J1939-11\nCAN 250 kbit/s, 능동 종단 (TBC)", "blue"),
]
H = 11


def bracket(d, y1, y2, label, color):
    x = 81
    d.ax.plot([x, x + 1.6, x + 1.6, x], [y1, y1, y2, y2], color=color, lw=1.6, zorder=3)
    d.text(x + 9.5, (y1 + y2) / 2, label, size=10, weight="bold", color=color)


def draw(d):
    P = d.P
    for y0, name, body, key in LAYERS:
        app = key == "purple"
        d.box(2, y0, 18, H, P["gray"], ec=P["accent"] if app else P["edge"])
        d.text(11, y0 + H / 2, name, size=10, weight="bold")
        d.box(22, y0, 56, H, P[key], ec=P["accent"] if app else P["edge"], lw=1.8 if app else 1.4)
        d.text(50, y0 + H / 2, body, size=10)
    bracket(d, 44, 44 + H, "ISOBUS\n고유 기능", P["accent"])
    bracket(d, 5, 31 + H, "J1939과\n조화된\n공통 기반", P["dim"])


diagram("18-isobus-layer-stack", draw, w=12, h=6.2, xmax=100, ymax=58)

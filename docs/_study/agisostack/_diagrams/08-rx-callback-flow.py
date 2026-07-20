"""CH8 §1 수신 경로 — CAN 프레임이 콜백까지 도달하는 흐름."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 20, 18, 12, P["brown"])
    d.text(11, 26, "CAN 버스\n원시 프레임", size=10)

    d.box(24, 20, 20, 12, P["gray"], ec=P["accent"], lw=1.6)
    d.text(34, 26, "CANHardwareInterface\n(수신 스레드)", size=9.8)

    d.box(48, 16, 22, 20, P["blue"])
    d.text(59, 32.5, "CANNetworkManager", size=10.5, weight="bold")
    d.text(59, 26, "· PGN 매칭\n· 목적지 주소 확인\n· TP/ETP 재조립", size=9.2, color=P["dim"])

    d.box(78, 30, 20, 10, P["green"])
    d.text(88, 35, "글로벌 PGN 콜백\n(브로드캐스트)", size=9.5)

    d.box(78, 12, 20, 10, P["purple"])
    d.text(88, 17, "파트너 PGN 콜백\n(목적지 지정)", size=9.5)

    d.arrow(20, 26, 24, 26)
    d.arrow(44, 26, 48, 26)
    d.arrow(70, 29, 78, 35, color=P["orange"])
    d.text(74, 27.2, "DA = 0xFF", size=8.2, color=P["orange"])
    d.arrow(70, 23, 78, 17, color=P["violet"])
    d.text(74, 24.8, "DA = 내 주소", size=8.2, color=P["violet"])

    # 콜백 시그니처
    d.box(56, 2, 42, 6.5, P["chip"])
    d.text(77, 5.2, "void cb(const isobus::CANMessage &, void *context)",
           size=9, color=P["dim"])
    d.arrow(88, 12, 88, 8.5, color=P["edge"], style="-", lw=1.0)


diagram("08-rx-callback-flow", draw, w=12.5, h=5.2, ymax=42)

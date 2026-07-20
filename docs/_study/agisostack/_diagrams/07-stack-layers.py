"""CH7 §0 ISOBUS 모듈의 3계층 — Hardware API / Networking API / Application."""
from _common import diagram


def draw(d):
    P = d.P

    # 3계층 스택
    d.box(30, 33, 40, 11, P["green"])
    d.text(50, 38.5, "Application\n(내 코드 — 수신 데이터 처리 · 송신 결정)", size=10.5)

    d.box(30, 19, 40, 11, P["blue"])
    d.text(50, 24.5, "Networking API\n(Control Function · 주소 클레임 · TP/ETP)", size=10.5)

    d.box(30, 5, 40, 11, P["brown"])
    d.text(50, 10.5, "Hardware API\n(CAN 트랜시버 드라이버 · 원시 CAN 프레임)", size=10.5)

    # 계층 간 화살표
    d.arrow(45, 30, 45, 33)
    d.arrow(55, 33, 55, 30)
    d.arrow(45, 16, 45, 19)
    d.arrow(55, 19, 55, 16)

    # 좌측 라이브러리 매핑
    d.box(2, 33, 24, 11, P["chip"])
    d.text(14, 38.5, "main.cpp", size=10, color=P["dim"])
    d.box(2, 19, 24, 11, P["chip"])
    d.text(14, 24.5, "CANNetworkManager\nInternalControlFunction", size=9.5, color=P["dim"])
    d.box(2, 5, 24, 11, P["chip"])
    d.text(14, 10.5, "CANHardwareInterface\nSocketCANInterface", size=9.5, color=P["dim"])

    d.arrow(26, 38.5, 30, 38.5, color=P["edge"], style="-", lw=1.2)
    d.arrow(26, 24.5, 30, 24.5, color=P["edge"], style="-", lw=1.2)
    d.arrow(26, 10.5, 30, 10.5, color=P["edge"], style="-", lw=1.2)

    # 우측 물리 버스
    d.box(78, 5, 20, 11, P["gray"], ec=P["accent"], lw=1.6)
    d.text(88, 10.5, "CAN 버스\n(250 kbit/s)", size=10)
    d.arrow(70, 10.5, 78, 10.5, color=P["accent"])
    d.arrow(78, 8, 70, 8, color=P["accent"])


diagram("07-stack-layers", draw, w=12, h=5.6, ymax=48)

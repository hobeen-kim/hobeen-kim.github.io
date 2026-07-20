"""CH17 §1 하드웨어 추상화 계층 — 스택 / CANHardwareInterface / CANHardwarePlugin / 실제 드라이버."""
from _common import diagram


def draw(d):
    P = d.P

    # 상단: 스택 코어
    d.box(24, 40, 52, 8, P["green"])
    d.text(50, 44, "CANNetworkManager (스택 코어 · 단일 스레드 처리)", size=10.5)

    # 중단: 하드웨어 인터페이스
    d.box(24, 27, 52, 9, P["blue"])
    d.text(50, 33, "CANHardwareInterface", size=11, weight="bold")
    d.text(50, 30, "채널 관리 · Rx/Tx 큐 · 스레드", size=9.5, color=P["dim"])

    d.arrow(42, 36, 42, 40)
    d.arrow(58, 40, 58, 36)

    # 추상 플러그인
    d.box(30, 16, 40, 7, P["purple"])
    d.text(50, 21, "CANHardwarePlugin (추상 기반 클래스)", size=10.5)
    d.text(50, 18, "open / close / read_frame / write_frame / get_is_valid", size=8.5, color=P["dim"])

    d.arrow(50, 27, 50, 23, style="-|>", color=P["edge"], lw=1.4)

    # 하단: 구체 드라이버들
    names = ["SocketCAN", "TWAI", "MCP2515", "PCANBasic", "MacCAN", "직접 구현"]
    x = 3
    for i, n in enumerate(names):
        fc = P["chip"] if i < 5 else P["brown"]
        d.box(x, 4, 14.5, 6, fc)
        d.text(x + 7.25, 7, n, size=9.5)
        d.arrow(x + 7.25, 10, 50, 16, color=P["edge"], style="-", lw=0.9, rad=0.12)
        x += 16

    d.text(50, 1.2, "CMake  -DCAN_DRIVER=<이름>  으로 선택", size=9, color=P["dim"])


diagram("17-hardware-layers", draw, w=12.5, h=6.2, ymax=50)

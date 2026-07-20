"""CH19 핵심 클래스 관계도 — CANNetworkManager를 중심으로 한 API 지도 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 중심
    d.box(36, 19, 28, 8, P["blue"], ec=P["accent"], lw=2.0)
    d.text(50, 24.4, "CANNetworkManager", size=12, weight="bold")
    d.text(50, 21.2, "싱글턴 · 송수신·프로토콜 구동", size=8.5, color=P["dim"])

    # 하드웨어 계층 (아래)
    d.box(36, 6, 28, 8, P["brown"])
    d.text(50, 11.4, "CANHardwareInterface", size=11, weight="bold")
    d.text(50, 8.2, "CANHardwarePlugin 구현체 연결", size=8.5, color=P["dim"])
    d.arrow(50, 14, 50, 19, color=P["accent"], lw=1.8, style="<|-|>")

    # Control Function 계열 (왼쪽 위)
    d.box(3, 14, 28, 20, P["gray"])
    d.text(17, 31.6, "Control Function", size=10.5, weight="bold", color=P["accent"])
    cf = [
        ("ControlFunction", "공통 기반 · 주소/NAME 조회"),
        ("InternalControlFunction", "내 ECU · 주소 클레임"),
        ("PartneredControlFunction", "상대 ECU · NAMEFilter 매칭"),
    ]
    for i, (name, sub) in enumerate(cf):
        y = 26.5 - i * 4.4
        d.box(4.5, y - 1.9, 25, 3.9, P["chip"], lw=0.9)
        d.text(17, y + 0.6, name, size=8.8, weight="bold")
        d.text(17, y - 1.1, sub, size=7.6, color=P["dim"])
    d.arrow(31, 24, 36, 24, color=P["accent"], lw=1.6)

    # NAME (왼쪽 아래)
    d.box(3, 4, 28, 7.5, P["purple"])
    d.text(17, 9.4, "NAME / NAMEFilter", size=10, weight="bold")
    d.text(17, 6.2, "64비트 신원 · 파트너 매칭 조건", size=8, color=P["dim"])
    d.arrow(17, 11.5, 17, 14, color=P["edge"], lw=1.4, ls="--")

    # 전송 프로토콜 (오른쪽 아래)
    d.box(69, 2, 28, 14, P["gray"])
    d.text(83, 13.6, "Transport Protocol", size=10.5, weight="bold", color=P["accent"])
    tp = [
        "TransportProtocolSessionBase",
        "TransportProtocolManager (TP)",
        "ExtendedTransportProtocolManager",
        "FastPacketProtocol (NMEA 2000)",
    ]
    for i, name in enumerate(tp):
        d.text(83, 10.6 - i * 2.4, name, size=8.2)
    d.arrow(69, 12, 64, 20, color=P["accent"], lw=1.5, rad=0.12)

    # 애플리케이션 계층 인터페이스 (오른쪽 위)
    d.box(69, 19, 28, 18, P["green"])
    d.text(83, 34.6, "애플리케이션 계층", size=10.5, weight="bold", color=P["accent"])
    app = [
        ("VirtualTerminalClient", "CH13"),
        ("TaskControllerClient / Server", "CH14·15"),
        ("ShortcutButtonInterface", "CH16"),
        ("SpeedMessagesInterface 등", "CH16"),
    ]
    for i, (name, ch) in enumerate(app):
        y = 31 - i * 3.1
        d.box(70.5, y - 1.4, 25, 2.9, P["chip"], lw=0.9)
        d.text(72, y, name, size=8.2, ha="left")
        d.text(94.5, y, ch, size=7.4, color=P["dim"], ha="right")
    d.arrow(69, 25, 64, 24, color=P["accent"], lw=1.6)


diagram("19-class-map", draw, w=13, h=5.4, ymax=39)

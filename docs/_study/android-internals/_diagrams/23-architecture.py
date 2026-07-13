"""CH23 agcand 전체 아키텍처 — CAN HW → SocketCAN → 데몬 → Binder → 앱 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # CAN 하드웨어
    d.box(2, 26, 16, 10, P["chip"])
    d.text(10, 31, "CAN 버스 HW\n(트랙터 ISOBUS)", size=8.5)

    # 커널 SocketCAN
    d.box(2, 10, 16, 10, P["gray"], ec=P["accent"], lw=1.4)
    d.text(10, 15, "커널 SocketCAN\n(can0, PF_CAN)", size=8.3)
    d.arrow(10, 26, 10, 20, color=P["orange"])

    # agcand (vendor)
    d.box(24, 8, 34, 30, P["green"], ec=P["accent"], lw=1.7)
    d.text(41, 35, "agcand (vendor)", size=10, weight="bold", color=P["accent"])
    d.box(27, 26, 28, 6, P["brown"])
    d.text(41, 29, "AgIsoStack++ (ISOBUS 스택)\ncc_library_static", size=7.8)
    d.box(27, 18, 28, 6, P["blue"])
    d.text(41, 21, "SocketCAN 수신 루프\n+ 프레임 캐시", size=7.8)
    d.box(27, 10, 28, 6, P["purple"])
    d.text(41, 13, "BnCanAccessService (ndk)\nAServiceManager_addService", size=7.6)
    d.arrow(18, 15, 27, 20, color=P["orange"])

    # servicemanager
    d.box(64, 26, 30, 8, P["gray"], ec=P["accent"], lw=1.4)
    d.text(79, 30, "vndservicemanager\n(vndbinder 등록)", size=8)
    d.arrow(55, 15, 64, 28, color=P["violet"], rad=-0.1)
    d.text(63, 21, "addService", size=7.5, color=P["violet"], ha="left")

    # 앱
    d.box(64, 10, 30, 10, P["blue"], ec=P["accent"], lw=1.4)
    d.text(79, 15, "앱 (Java)\nICanAccessService 프록시로 구독", size=8)
    d.arrow(58, 13, 64, 14, color=P["orange"])
    d.text(61, 11, "Binder", size=7.5, color=P["orange"])
    d.arrow(79, 26, 79, 20, color=P["dim"], rad=0.0, ls="--")
    d.text(88, 23, "getService", size=7.5, color=P["dim"])

    d.text(50, 5, "CAN 프레임이 데몬을 거쳐 Binder로 앱까지 흐른다", size=8.5, color=P["dim"])


diagram("23-architecture", draw, w=13.5, h=6.0, xmax=100, ymax=40)

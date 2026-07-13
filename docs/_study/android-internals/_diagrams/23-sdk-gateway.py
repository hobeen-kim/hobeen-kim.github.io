"""CH23 §일반 앱에 개방하기 — 게이트웨이·SDK 구조 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 일반 앱 그룹
    d.box(2, 10, 26, 24, P["gray"], ec=P["edge"])
    d.text(15, 31, "일반 앱 (자체 마켓 설치)", size=10, color=P["dim"])

    d.box(4, 21, 22, 7, P["chip"])
    d.text(15, 24.5, "앱 코드", size=10)

    d.box(4, 12, 22, 7, P["blue"])
    d.text(15, 15.5, "ag-sdk.aar\n(AgVehicleManager)", size=9.5)

    # 게이트웨이
    d.box(40, 12, 24, 18, P["green"])
    d.text(52, 24.5, "AgVehicleService", size=10.5, weight="bold")
    d.text(52, 19.5, "platform 서명 시스템 앱\ngetCallingUid 권한 판정", size=9)

    # vendor 데몬
    d.box(76, 14, 20, 14, P["purple"])
    d.text(86, 21, "agcand\n(vendor 데몬)", size=10)

    # 화살표
    d.arrow(28, 20, 40, 20)
    d.text(34, 23.5, "bindService()", size=9, color=P["accent"])
    d.text(34, 16.5, "공개 SDK API", size=8.5, color=P["dim"])

    d.arrow(64, 20, 76, 20, color=P["orange"])
    d.text(70, 23.5, "AIDL / Binder", size=9, color=P["orange"])
    d.text(70, 16.5, "hidden API·platform 전용", size=8.5, color=P["dim"])

    # 권한 라벨
    d.text(52, 8, "permission: farm.agmo.permission.CAN_ACCESS (signature|privileged)",
           size=8.5, color=P["dim"])


diagram("23-sdk-gateway", draw, w=13, h=5, ymax=36)

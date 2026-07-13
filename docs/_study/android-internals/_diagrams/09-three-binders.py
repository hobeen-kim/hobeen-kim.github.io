"""CH9 세 개의 Binder 도메인 — framework·vnd·hw 분리 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    domains = [
        ("/dev/binder", "framework binder", P["blue"],
         ["앱 프로세스", "system_server", "servicemanager"], 2),
        ("/dev/vndbinder", "vendor binder", P["brown"],
         ["vendor 데몬 A", "vendor 데몬 B", "vndservicemanager"], 35),
        ("/dev/hwbinder", "hw binder", P["green"],
         ["HAL 서버", "클라이언트", "hwservicemanager"], 68),
    ]

    for node, sub, fc, members, x in domains:
        d.box(x, 8, 29, 32, P["gray"], ec=P["accent"], lw=1.5)
        d.box(x + 2, 33, 25, 5.5, fc)
        d.text(x + 14.5, 35.75, node, size=10, weight="bold")
        d.text(x + 14.5, 30.5, sub, size=8.3, color=P["dim"])
        for i, m in enumerate(members):
            d.box(x + 4, 24 - i * 6, 21, 4.6, fc)
            d.text(x + 14.5, 24 - i * 6 + 2.3, m, size=8.3)

    # 네이티브 vendor 데몬 위치 강조
    d.text(49.5, 43, "Treble 이후: 네이티브 vendor 데몬(예: CAN 데몬)은 /dev/vndbinder를 쓴다",
           size=9, color=P["orange"])
    d.text(50, 4, "세 도메인은 커널 드라이버 인스턴스가 분리돼 서로 통신하지 못한다",
           size=8, color=P["dim"])


diagram("09-three-binders", draw, w=12.5, h=5.6, xmax=100, ymax=47)

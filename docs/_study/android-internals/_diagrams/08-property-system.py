"""CH8 시스템 프로퍼티 구조 — 로드·저장·읽기 경로 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽: prop 소스 파일들
    d.box(2, 22, 24, 24, P["chip"])
    d.text(14, 43.5, "prop 소스 파일", size=9.5, weight="bold", color=P["dim"])
    for i, s in enumerate([
        "/system/build.prop",
        "/vendor/build.prop",
        "/odm · /product",
        "default.prop(ramdisk)",
        "persist.* (/data)",
    ]):
        d.box(4, 39 - i * 3.3, 20, 2.7, P["blue"])
        d.text(14, 39 - i * 3.3 + 1.35, s, size=7.8)

    # 가운데: property_service (init 내부)
    d.box(34, 20, 30, 24, P["gray"], ec=P["accent"], lw=1.7)
    d.text(49, 41, "property_service", size=11, weight="bold", color=P["accent"])
    d.text(49, 37.5, "(init 스레드)", size=8.3, color=P["dim"])
    d.box(37, 27, 24, 8, P["purple"])
    d.text(49, 31, "property store\n/dev/__properties__\n(공유 메모리 · mmap)", size=8.3)
    d.box(37, 21.5, 24, 4, P["brown"])
    d.text(49, 23.5, "property_service 소켓", size=8.3)

    # 오른쪽: 클라이언트
    d.box(72, 30, 26, 14, P["chip"])
    d.text(85, 41.5, "읽기 클라이언트", size=9.5, weight="bold", color=P["dim"])
    d.text(85, 36.5, "__system_property_get()\ngetprop · ro.* 캐시", size=8.3)

    d.box(72, 20, 26, 7, P["chip"])
    d.text(85, 23.5, "쓰기: setprop / SetProperty()", size=8.3)

    # 화살표
    d.arrow(26, 34, 34, 34, color=P["accent"])
    d.text(30, 35.8, "부팅 시\n로드", size=7.5, color=P["dim"])
    d.arrow(61, 33, 72, 36, color=P["orange"])
    d.text(67, 36.2, "mmap 읽기", size=7.5, color=P["orange"])
    d.arrow(72, 23.5, 61.2, 23.5, color=P["violet"])
    d.text(66, 25.2, "소켓 요청", size=7.5, color=P["violet"])
    d.arrow(49, 27, 49, 25.5, color=P["violet"])

    # 트리거 주석
    d.text(49, 17.5, "특정 prop이 바뀌면 on property:ro.x=1 트리거로 액션 실행",
           size=8, color=P["dim"])


diagram("08-property-system", draw, w=12.5, h=5.6, xmax=100, ymax=48)

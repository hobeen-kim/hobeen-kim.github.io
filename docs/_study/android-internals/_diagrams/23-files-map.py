"""CH23 프로젝트 파일 배치도 — vendor/<회사>/agcand 트리 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 루트
    d.box(3, 42, 50, 6, P["gray"], ec=P["accent"], lw=1.6)
    d.text(28, 45, "vendor/agmo/agcand/", size=10, weight="bold", color=P["accent"])

    files = [
        ("Android.bp", "빌드 규칙: cc_binary · aidl_interface · cc_library_static", P["green"]),
        ("aidl/.../ICanAccessService.aidl", "Binder 인터페이스 + parcelable CanFrame", P["purple"]),
        ("src/main.cpp", "데몬 진입점 · 스레드풀 · addService · 수신 루프", P["blue"]),
        ("src/CanAccessService.cpp", "BnCanAccessService 구현", P["blue"]),
        ("external/AgIsoStack/", "포팅한 ISOBUS 스택 소스", P["brown"]),
        ("agcand.rc", "init: class hal · user/group · capabilities", P["green"]),
        ("sepolicy/agcand.te", "도메인 규칙 (avc allow)", P["purple"]),
        ("sepolicy/file_contexts", "실행 파일 → 도메인 라벨", P["purple"]),
        ("sepolicy/service_contexts", "서비스명 → 라벨", P["purple"]),
        ("manifest_agcand.xml", "vintf_fragments (VINTF 등록)", P["brown"]),
    ]
    y = 38
    for name, desc, fc in files:
        d.box(8, y, 26, 3.4, fc)
        d.text(9.5, y + 1.7, name, size=8, ha="left")
        d.text(37, y + 1.7, desc, size=7.8, ha="left", color=P["dim"])
        y -= 3.8

    d.text(28, 1.5, "PRODUCT_PACKAGES += agcand 로 제품에 포함", size=8, color=P["orange"])


diagram("23-files-map", draw, w=13, h=6.6, xmax=100, ymax=50)

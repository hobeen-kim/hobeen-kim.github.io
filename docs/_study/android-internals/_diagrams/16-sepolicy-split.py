"""CH16 sepolicy 분리 — Treble의 플랫폼/벤더 정책이 부팅 시 결합 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 정책 소스
    d.box(4, 34, 40, 12, P["blue"])
    d.text(24, 42.5, "플랫폼 정책 (Google 소유)", size=10, weight="bold")
    d.text(24, 37.5, "system/sepolicy/\npublic · private · vendor", size=9,
           color=P["dim"])

    d.box(56, 34, 40, 12, P["green"])
    d.text(76, 42.5, "벤더 정책 (device 소유)", size=10, weight="bold")
    d.text(76, 37.5, "device/agmo/tractor/sepolicy/\nBOARD_VENDOR_SEPOLICY_DIRS", size=9,
           color=P["dim"])

    # CIL 컴파일 산출
    d.box(9, 20, 30, 8, P["brown"])
    d.text(24, 24, "plat_sepolicy.cil\n(/system)", size=9)
    d.box(61, 20, 30, 8, P["brown"])
    d.text(76, 24, "vendor_sepolicy.cil\n(/vendor)", size=9)

    # 결합
    d.box(30, 4, 40, 9, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 8.5, "부팅 시 secilc 결합 → 커널 로드", size=10, weight="bold")

    # 화살표
    d.arrow(24, 34, 24, 28, color=P["accent"])
    d.arrow(76, 34, 76, 28, color=P["accent"])
    d.arrow(24, 20, 42, 13, color=P["orange"])
    d.arrow(76, 20, 58, 13, color=P["orange"])


diagram("16-sepolicy-split", draw, w=13, h=5.2, xmax=100, ymax=50)

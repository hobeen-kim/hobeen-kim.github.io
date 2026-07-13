"""CH2 Device Tree — DTS→DTB/DTBO 빌드와 커널 하드웨어 발견 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 소스
    d.box(3, 58, 22, 12, P["blue"])
    d.text(14, 64, ".dts / .dtsi\n(보드 소스)", size=9.5)
    d.box(3, 40, 22, 12, P["blue"])
    d.text(14, 46, "overlay .dts\n(파생/변형)", size=9.5)

    # dtc 컴파일
    d.box(32, 49, 16, 12, P["purple"])
    d.text(40, 55, "dtc\n컴파일", size=10, weight="bold")

    # 바이너리 산출물
    d.box(55, 58, 20, 12, P["brown"])
    d.text(65, 64, ".dtb\n(base blob)", size=9.5)
    d.box(55, 40, 20, 12, P["brown"])
    d.text(65, 46, ".dtbo\n(dtbo 파티션)", size=9.5)

    d.arrow(25, 64, 32, 57, color=P["accent"])
    d.arrow(25, 46, 32, 53, color=P["accent"])
    d.arrow(48, 56, 55, 63, color=P["accent"])
    d.arrow(48, 54, 55, 47, color=P["accent"])

    # 부트로더 병합
    d.box(82, 49, 15, 12, P["green"])
    d.text(89.5, 55, "부트로더\nDTB+DTBO\n병합", size=8.8)
    d.arrow(75, 64, 82, 57, color=P["orange"])
    d.arrow(75, 46, 82, 53, color=P["orange"])

    # 커널 파싱 → 디바이스 발견 (하단 트리)
    d.box(30, 20, 40, 9, P["gray"], ec=P["accent"], lw=1.6)
    d.text(50, 24.5, "커널이 DT 파싱 → 드라이버 probe", size=10.5, weight="bold",
           color=P["accent"])
    d.arrow(89.5, 49, 55, 29, color=P["orange"], rad=0.2)

    leaves = [
        (12, "soc { }\n버스·클럭"),
        (32, "i2c@ { }\n온도 센서"),
        (52, "spi@ { }\nCAN 컨트롤러"),
        (72, "chosen { }\n부트 인자"),
        (90, "memory { }\nRAM 맵"),
    ]
    for lx, label in leaves:
        d.box(lx - 8, 4, 16, 9, P["chip"])
        d.text(lx, 8.5, label, size=8.3)
        d.arrow(50, 20, lx, 13, color=P["dim"], rad=0.05, lw=1.1)


diagram("02-device-tree", draw, w=12, h=7.5, xmax=100, ymax=74)

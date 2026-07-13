"""CH2 SoC 블록도 — 한 칩 안의 주요 IP 블록 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # SoC 외곽
    d.box(6, 10, 66, 78, P["gray"], ec=P["accent"], lw=1.8)
    d.text(39, 84.5, "SoC (Application Processor)", size=12, weight="bold",
           color=P["accent"])

    # 상단 연산 블록
    d.box(10, 68, 26, 12, P["blue"])
    d.text(23, 74, "CPU big 클러스터\n(고성능 코어)", size=9.5)
    d.box(42, 68, 26, 12, P["blue"])
    d.text(55, 74, "CPU LITTLE 클러스터\n(저전력 코어)", size=9.5)

    d.box(10, 53, 17, 11, P["green"])
    d.text(18.5, 58.5, "GPU", size=10)
    d.box(30, 53, 17, 11, P["green"])
    d.text(38.5, 58.5, "NPU/DSP", size=9.5)
    d.box(51, 53, 17, 11, P["green"])
    d.text(59.5, 58.5, "ISP\n(카메라)", size=9.5)

    # 인터커넥트 버스
    d.box(10, 44, 58, 6, P["purple"])
    d.text(39, 47, "온칩 인터커넥트 (버스/NoC)", size=10, weight="bold")

    # 하단 I/O·컨트롤러
    d.box(10, 29, 17, 11, P["brown"])
    d.text(18.5, 34.5, "모뎀\n(셀룰러)", size=9.5)
    d.box(30, 29, 17, 11, P["brown"])
    d.text(38.5, 34.5, "메모리\n컨트롤러", size=9.5)
    d.box(51, 29, 17, 11, P["brown"])
    d.text(59.5, 34.5, "주변장치\nI/O 컨트롤러", size=9)

    d.box(10, 14, 58, 11, P["chip"])
    d.text(39, 19.5, "보안·부트: BootROM(PBL) · TrustZone(EL3) · 크립토엔진", size=9.5)

    # 인터커넥트 ↔ 각 블록
    for cx in (23, 55):
        d.arrow(cx, 68, cx, 50, color=P["accent"], style="<|-|>", lw=1.2)
    for cx in (18.5, 38.5, 59.5):
        d.arrow(cx, 53, cx, 50, color=P["accent"], style="<|-|>", lw=1.2)
        d.arrow(cx, 44, cx, 40, color=P["accent"], style="<|-|>", lw=1.2)

    # 외부 메모리·스토리지
    d.box(80, 55, 16, 12, P["chip"])
    d.text(88, 61, "LPDDR\nDRAM", size=9.5)
    d.box(80, 34, 16, 12, P["chip"])
    d.text(88, 40, "UFS / eMMC\n스토리지", size=9)
    d.arrow(72, 34.5, 80, 40, color=P["orange"], style="<|-|>")
    d.arrow(72, 40, 80, 55, color=P["orange"], style="<|-|>", rad=-0.1)
    d.text(76, 50, "외부 버스", size=8, color=P["orange"])


diagram("02-soc-block", draw, w=11, h=9, xmax=100, ymax=95)

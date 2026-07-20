"""CH02 1바이트 주소 공간 — 일반 주소 / NULL(254) / 브로드캐스트(255) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.text(4, 34.5, "1바이트 주소 공간 (0 ~ 255)", size=11, weight="bold",
           color=P["accent"], ha="left")

    # 0~253
    d.box(4, 18, 66, 12, P["blue"])
    d.text(37, 25.6, "0 ~ 253", size=12, weight="bold")
    d.text(37, 21.4, "제어 장치가 실제로 점유하는 주소", size=9, color=P["dim"])

    # 254
    d.box(72, 18, 11, 12, P["brown"])
    d.text(77.5, 25.6, "254", size=12, weight="bold")
    d.text(77.5, 21.4, "0xFE", size=8.5, color=P["dim"])

    # 255
    d.box(85, 18, 11, 12, P["purple"])
    d.text(90.5, 25.6, "255", size=12, weight="bold")
    d.text(90.5, 21.4, "0xFF", size=8.5, color=P["dim"])

    # 설명 칩
    d.box(72, 4, 11, 11, P["chip"])
    d.text(77.5, 11.5, "NULL", size=9, weight="bold", color=P["orange"])
    d.text(77.5, 7.2, "주소가\n아직 없을 때", size=7.6, color=P["dim"])

    d.box(85, 4, 11, 11, P["chip"])
    d.text(90.5, 11.5, "브로드캐스트", size=8.2, weight="bold", color=P["violet"])
    d.text(90.5, 7.2, "모두에게\n보낼 때", size=7.6, color=P["dim"])

    d.box(4, 4, 66, 11, P["chip"])
    d.text(37, 11.5, "주소 클레임으로 확보한다", size=9.5, weight="bold")
    d.text(37, 7.2, "언제든 바뀔 수 있으므로 주소만으로 상대를 식별하면 안 된다",
           size=8.2, color=P["dim"])

    d.arrow(77.5, 18, 77.5, 15.4, color=P["orange"], lw=1.4)
    d.arrow(90.5, 18, 90.5, 15.4, color=P["violet"], lw=1.4)
    d.arrow(37, 18, 37, 15.4, color=P["accent"], lw=1.4)


diagram("02-address-space", draw, w=11.5, h=4.4, ymax=38)

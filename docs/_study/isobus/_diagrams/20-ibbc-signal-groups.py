"""20장 2절: IBBC 9핀이 나르는 세 묶음(CAN, 전원 두 계열, TBC용 선) (light/dark PNG)."""
from _common import diagram

LANES = [
    # (y, 그룹, 신호, 트랙터 쪽, 작업기 쪽, 색 키, 화살표 모양)
    (38, "CAN", "CAN_H · CAN_L", "작업기 버스", "작업기 버스 연장", "blue", "<|-|>"),
    (28, "전원", "PWR · GND", None, "밸브·모터 (액추에이터)\n12 V에서 최소 50 A", "brown", "-|>"),
    (19, "전원", "ECU_PWR · ECU_GND", None, "작업기 ECU·센서\n12 V에서 최소 15 A", "brown", "-|>"),
    (9, "종단 제어", "TBC_PWR · TBC_RTN · TBC_DIS", "TBC 전원\n(ECU_PWR 또는 TECU)",
     "종단 바이어스 회로(TBC)용", "purple", "-"),
]
CH = 7


def draw(d):
    P = d.P
    d.box(2, 3, 25, 44, P["gray"], ec=P["edge"])
    d.text(14.5, 44, "트랙터", size=11, weight="bold")
    d.box(73, 3, 25, 44, P["gray"], ec=P["edge"])
    d.text(85.5, 44, "작업기", size=11, weight="bold")
    d.box(34, 3, 32, 44, P["chip"], ec=P["accent"], lw=1.8)
    d.text(50, 44, "IBBC (9핀)", size=11, weight="bold")

    d.box(4, 15.5, 21, 16, P["purple"])
    d.text(14.5, 23.5, "TECU\n(전원 분배·제어)", size=9.5)

    for y, group, signals, src, dst, key, style in LANES:
        d.box(36, y - CH / 2, 28, CH, P[key])
        d.text(50, y + 1.4, group, size=8.5, color=P["dim"])
        d.text(50, y - 1.3, signals, size=9.5, weight="bold")
        if src:
            d.box(4, y - CH / 2, 21, CH, P["chip"])
            d.text(14.5, y, src, size=9)
        d.box(75, y - CH / 2, 21, CH, P["chip"])
        d.text(85.5, y, dst, size=9)
        d.arrow(25, y, 36, y, lw=1.6, style=style)
        d.arrow(64, y, 75, y, lw=1.6, style=style)


diagram("20-ibbc-signal-groups", draw, w=12.5, h=5.8, xmax=100, ymax=50)

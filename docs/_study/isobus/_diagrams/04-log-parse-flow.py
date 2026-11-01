"""CH4 7절 CAN 로그 한 줄을 ID와 Data로 나누고 각각 다시 쪼개는 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(x, y, w, h, label, fc, size=10, weight="normal"):
        d.box(x, y, w, h, fc)
        d.text(x + w / 2, y + h / 2, label, size=size, weight=weight)

    node(2, 19, 25, 9, "CAN 로그\n0CF004FE#FF3C320000FFFF00", P["gray"], size=9.6, weight="bold")
    node(34, 31, 20, 8, "CAN ID\n0x0CF004FE", P["blue"], size=10.5, weight="bold")
    node(34, 8, 24, 8, "Data\nFF 3C 32 00 00 FF FF 00", P["green"], size=10, weight="bold")
    d.arrow(27, 25, 34, 34.5, color=P["accent"])
    d.arrow(27, 22, 34, 12.5, color=P["accent"])

    id_leaves = [(40.5, "Priority: 3 (상위 3bit)"), (33, "PGN: 0xF004 = EEC1 엔진 속도"),
                 (25.5, "Source: 0xFE = 주소 254")]
    for y, label in id_leaves:
        node(66, y, 31, 5.6, label, P["chip"], size=9.8)
        d.arrow(54, 35, 66, y + 2.8, color=P["edge"], lw=1.4)

    data_leaves = [(17, "Byte 0~2: 토크 정보"), (9.5, "Byte 3~4: 엔진 RPM"), (2, "Byte 5~7: 기타")]
    for y, label in data_leaves:
        node(66, y, 31, 5.6, label, P["chip"], size=9.8)
        d.arrow(58, 12, 66, y + 2.8, color=P["edge"], lw=1.4)


diagram("04-log-parse-flow", draw, w=12, h=5.65, xmax=100, ymax=47)

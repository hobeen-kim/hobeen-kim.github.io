"""CH8 §4 TP/ETP 재조립 — 다중 프레임도 같은 콜백 하나로 도착한다."""
from _common import diagram


def draw(d):
    P = d.P

    # 버스 위의 다중 프레임
    d.text(4, 34, "CAN 버스", size=10, color=P["dim"], ha="left")
    labels = ["BAM", "DT 1", "DT 2", "…", "DT 255"]
    for i, lb in enumerate(labels):
        x = 4 + i * 11
        d.box(x, 26, 9, 6, P["brown"])
        d.text(x + 4.5, 29, lb, size=9)

    # 스택 재조립
    d.box(4, 13, 55, 9, P["blue"])
    d.text(31.5, 17.5, "CANNetworkManager — TP/ETP 세션 재조립", size=10.5)
    for i in range(5):
        d.arrow(8.5 + i * 11, 26, 8.5 + i * 11, 22, color=P["edge"], lw=1.2)

    # 단일 콜백
    d.box(68, 13, 28, 9, P["green"])
    d.text(82, 17.5, "propa_callback 1회 호출", size=10.5)
    d.arrow(59, 17.5, 68, 17.5, color=P["accent"])

    d.box(68, 2, 28, 8, P["chip"])
    d.text(82, 6, "get_data_length() → 1785", size=9.5, color=P["dim"])
    d.arrow(82, 13, 82, 10, color=P["edge"], style="-", lw=1.0)


diagram("08-tp-reassembly", draw, w=12.5, h=4.6, ymax=38)

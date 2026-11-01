"""CH2 3절 메시지 기반 브로드캐스트: 한 메시지를 모든 노드가 받고 필요한 ID만 골라 쓴다 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax
    by = 24

    # 송신 노드와 메시지
    d.box(4, 31, 17, 7, P["blue"])
    d.text(12.5, 34.5, "엔진 ECU", size=11, weight="bold")
    d.arrow(12.5, 31, 12.5, by + 0.4, color=P["accent"], lw=2.2)
    d.box(15, 25.8, 29, 4.6, P["chip"], ec=P["accent"], lw=1.6)
    d.text(29.5, 28.1, "ID=0x100, 데이터=RPM:2000", size=10)

    # 버스
    ax.plot([4, 96], [by, by], color=P["accent"], lw=3.4, zorder=2)
    d.text(95, by + 2, "CAN 버스", size=9.5, color=P["dim"], ha="right")

    # 수신 노드
    receivers = [
        (34, "계기판 ECU", "0x100 필요 → RPM 표시", True),
        (58, "변속기 ECU", "0x100 필요 → 기어 결정", True),
        (82, "ABS ECU", "0x100 불필요 → 무시", False),
    ]
    for x, name, note, use in receivers:
        d.arrow(x, by - 0.4, x, 17.4, color=P["accent"] if use else P["edge"], lw=1.8)
        d.box(x - 10, 11, 20, 6.4, P["blue"] if use else P["gray"])
        d.text(x, 14.2, name, size=10.5, weight="bold", color=P["text"] if use else P["dim"])
        d.text(x, 7.6, note, size=10, color=P["accent"] if use else P["dim"])


diagram("02-broadcast-filter", draw, w=12, h=4.8, xmax=100, ymax=40)

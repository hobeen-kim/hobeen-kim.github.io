"""CH5 2절 비트 단위 중재 순서: 노드A(0x100)와 노드B(0x200)가 버스에 비트를 보내고 다시 읽는다 (light/dark PNG)."""
from _common import diagram

XA, XBUS, XB = 18, 50, 82
HEAD_Y, HEAD_H = 66, 7
ROWS = [
    # (row label, A sends, B sends, bus, A result, B result, B loses)
    ("SOF", "SOF", "SOF", None, None, None, False),
    ("비트10", "0 (D)", "0 (D)", "0", "0 읽음: 일치", "0 읽음: 일치", False),
    ("비트9", "0 (D)", "1 (R)", "0", "0 읽음: 일치, 계속", "0 읽음: 불일치, 즉시 중단", True),
]
ROW_Y = [59, 47, 32]


def draw(d):
    P = d.P
    ax = d.ax

    for x, title, sub in ((XA, "노드A", "ID 0x100"), (XBUS, "CAN 버스", "Wired-AND"),
                          (XB, "노드B", "ID 0x200")):
        d.box(x - 12, HEAD_Y, 24, HEAD_H, P["blue"] if x != XBUS else P["green"])
        d.text(x, HEAD_Y + HEAD_H * 0.64, title, size=10.5, weight="bold")
        d.text(x, HEAD_Y + HEAD_H * 0.27, sub, size=8.3, color=P["dim"])
        ax.plot([x, x], [HEAD_Y - 0.5, 4], color=P["edge"], lw=1.0, ls=(0, (4, 4)), zorder=1)

    for (label, a_tx, b_tx, bus, a_res, b_res, b_loses), y in zip(ROWS, ROW_Y):
        d.text(2, y, label, size=9, color=P["dim"], ha="left", weight="bold")
        d.arrow(XA, y, XBUS - 4, y, color=P["accent"])
        d.text((XA + XBUS) / 2 - 2, y + 1.8, a_tx, size=9)
        d.arrow(XB, y, XBUS + 4, y, color=P["violet"])
        d.text((XB + XBUS) / 2 + 2, y + 1.8, b_tx, size=9)
        if bus is None:
            continue
        d.box(XBUS - 4, y - 2.2, 8, 4.4, P["chip"], ec=P["accent"], lw=1.4)
        d.text(XBUS, y, bus, size=10, weight="bold")
        ry = y - 5.5
        d.arrow(XBUS - 4, ry, XA + 0.5, ry, color=P["dim"], lw=1.3, ls="--")
        d.text((XA + XBUS) / 2 - 2, ry - 1.9, a_res, size=8.6,
               color=P["accent"] if b_loses else P["dim"], weight="bold" if b_loses else "normal")
        d.arrow(XBUS + 4, ry, XB - 0.5, ry, color=P["dim"], lw=1.3, ls="--")
        d.text((XB + XBUS) / 2 + 2, ry - 1.9, b_res, size=8.6,
               color=P["orange"] if b_loses else P["dim"], weight="bold" if b_loses else "normal")

    d.box(XA - 15, 6, 30, 9, P["green"])
    d.text(XA, 12.2, "나머지 프레임 전송", size=9.5, weight="bold")
    d.text(XA, 8.6, "비트8~0, DLC, Data ... EOF", size=8.4, color=P["dim"])
    d.box(XB - 15, 6, 30, 9, P["gray"])
    d.text(XB, 12.2, "수신만 하며 대기", size=9.5, weight="bold")
    d.text(XB, 8.6, "버스가 비면 처음부터 재전송", size=8.4, color=P["dim"])


diagram("05-arbitration-sequence", draw, w=12, h=7.4, xmax=100, ymax=75)

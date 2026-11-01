"""CH7 2절 CAN FD 프레임 흐름: 중재 구간은 표준 속도, BRS 뒤 데이터 구간은 고속, ACK부터 표준 속도 복귀 (light/dark PNG)."""
from _common import diagram

XT, XBUS, XR = 14, 44, 74
HEAD_Y, HEAD_H = 72, 6
BAND_X0, BAND_X1 = 2, 98


def draw(d):
    P = d.P
    ax = d.ax
    ax.set_ylim(15, 80)

    bands = ((57, 70, P["gray"], "Arbitration phase", "모든 노드 같은 속도"),
             (35.5, 57, P["blue"], "Data phase", "고속 전송"),
             (27, 35.5, P["gray"], "표준 속도 복귀", ""))
    for y0, y1, fc, name, sub in bands:
        d.box(BAND_X0, y0, BAND_X1 - BAND_X0, y1 - y0, fc, ec=fc, lw=0.5, r=0.0, alpha=0.6)
        d.text(BAND_X1 - 1.5, y1 - 2.4, name, size=9.2, weight="bold", ha="right")
        if sub:
            d.text(BAND_X1 - 1.5, y1 - 5.0, sub, size=8.4, ha="right", color=P["dim"])

    for x, title in ((XT, "송신 노드"), (XBUS, "CAN 버스"), (XR, "수신 노드")):
        d.box(x - 10, HEAD_Y, 20, HEAD_H, P["green"] if x == XBUS else P["chip"])
        d.text(x, HEAD_Y + HEAD_H / 2, title, size=10.2, weight="bold")
        ax.plot([x, x], [HEAD_Y - 0.5, 18], color=P["edge"], lw=1.0, ls=(0, (4, 4)), zorder=3)

    def send(y, s, color=None, bold=False):
        d.arrow(XT, y, XBUS - 0.6, y, color=color or P["accent"])
        d.text((XT + XBUS) / 2, y + 1.7, s, size=8.6, weight="bold" if bold else "normal")

    send(66, "SOF + Arbitration ID (표준 속도)")
    send(60, "FDF=1, BRS=1 (CAN FD, 비트레이트 전환)", color=P["orange"], bold=True)
    d.arrow(XBUS, 54, XT + 0.6, 54, color=P["dim"], lw=1.3, ls="--")
    d.text((XT + XBUS) / 2, 55.7, "BRS 이후 고속 전환", size=8.6, color=P["dim"])
    send(47, "ESI + DLC + Data (64바이트, 고속)")
    send(40, "CRC (17/21비트)")
    send(31, "ACK + EOF (표준 속도 복귀)")
    d.arrow(XBUS, 22, XR - 0.6, 22, color=P["violet"])
    d.text((XBUS + XR) / 2, 23.7, "수신 완료", size=8.6)


diagram("07-canfd-frame-flow", draw, w=11, h=5.4, xmax=100, ymax=80)

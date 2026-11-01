"""CH6 2절 에러 프레임 이후 흐름: 오류 감지, 에러 플래그 겹침, Delimiter, 재전송 (light/dark PNG)."""
from _common import diagram

XT, XBUS, XR = 16, 50, 84
HEAD_Y, HEAD_H = 72, 6


def note(d, x, y, s, fc, w=30, h=4.6, color=None):
    P = d.P
    d.box(x - w / 2, y - h / 2, w, h, fc, ec=P["edge"], lw=1.0)
    d.text(x, y, s, size=8.8, color=color)


def draw(d):
    P = d.P
    ax = d.ax

    for x, title in ((XT, "송신 노드"), (XBUS, "CAN 버스"), (XR, "수신 노드")):
        d.box(x - 11, HEAD_Y, 22, HEAD_H, P["green"] if x == XBUS else P["blue"])
        d.text(x, HEAD_Y + HEAD_H / 2, title, size=10.5, weight="bold")
        ax.plot([x, x], [HEAD_Y - 0.5, 3], color=P["edge"], lw=1.0, ls=(0, (4, 4)), zorder=1)

    y = 66
    d.arrow(XT, y, XBUS - 0.6, y, color=P["accent"])
    d.text((XT + XBUS) / 2, y + 1.8, "데이터 프레임 전송 중", size=8.8)

    y = 60
    note(d, XBUS, y, "비트 오류 발생", P["chip"], w=20, color=P["orange"])

    y = 53
    d.arrow(XT, y, XBUS - 0.6, y, color=P["orange"])
    d.text((XT + XBUS) / 2, y + 1.8, "Active Error Flag (6× Dominant)", size=8.8)

    y = 46
    d.arrow(XR, y, XBUS + 0.6, y, color=P["violet"])
    d.text((XR + XBUS) / 2, y + 1.8, "자신의 Error Flag 추가 전송", size=8.8)

    y = 39
    note(d, XBUS, y, "Superimposed Error Flags\n(겹친 에러 플래그, Dominant 6~12비트)", P["chip"], w=34, h=7.4)

    y = 29
    d.arrow(XBUS, y, XT + 0.6, y, color=P["dim"], lw=1.3, ls="--")
    d.text((XT + XBUS) / 2, y + 1.8, "Error Delimiter 감지", size=8.8, color=P["dim"])
    d.arrow(XBUS, y, XR - 0.6, y, color=P["dim"], lw=1.3, ls="--")
    d.text((XR + XBUS) / 2, y + 1.8, "Error Delimiter 감지", size=8.8, color=P["dim"])

    y = 20
    note(d, XT, y, "Interframe Space 후", P["chip"], w=22)

    y = 11
    d.arrow(XT, y, XBUS - 0.6, y, color=P["accent"])
    d.text((XT + XBUS) / 2, y + 1.8, "오류 난 프레임 재전송 시도", size=8.8,
           color=P["accent"], weight="bold")


diagram("06-error-flag-sequence", draw, w=11, h=7.0, xmax=100, ymax=80)

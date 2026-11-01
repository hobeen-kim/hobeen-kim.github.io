"""54장 5절: SCMasterStatus 주기와 타임아웃 (활동 상태 200 ms/600 ms, Ready 1 s/3 s, light/dark PNG)."""
from _common import diagram

SENT = [24, 34, 44, 54]
LOST = [64, 74]
TIMEOUT_X = 84


def row(d, cy, label, period, timeout):
    P = d.P
    d.text(2, cy, label, size=9.5, ha="left")
    d.ax.plot([20, 97], [cy - 4, cy - 4], color=P["edge"], lw=1.0, zorder=1)

    for x in SENT:
        d.box(x - 1.3, cy - 4, 2.6, 7, P["blue"], r=0.005)
    for x in LOST:
        d.box(x - 1.3, cy - 4, 2.6, 7, P["bg"], ec=P["edge"], lw=1.0, r=0.005)
        d.ax.plot([x - 1.3, x + 1.3], [cy - 4, cy + 3], color=P["edge"], lw=1.0, zorder=3)

    # 주기
    d.ax.plot([SENT[0], SENT[1]], [cy + 5, cy + 5], color=P["dim"], lw=1.0)
    d.text((SENT[0] + SENT[1]) / 2, cy + 7, period, size=8.5, color=P["dim"])
    d.text((LOST[0] + LOST[1]) / 2, cy + 7, "끊김", size=8.5, color=P["dim"])

    # 마지막 메시지에서 타임아웃까지
    d.ax.plot([SENT[-1], SENT[-1], TIMEOUT_X, TIMEOUT_X], [cy - 6, cy - 7.5, cy - 7.5, cy - 6],
              color=P["orange"], lw=1.3)
    d.text((SENT[-1] + TIMEOUT_X) / 2, cy - 9.6, f"{timeout} (주기의 3배)", size=8.5, color=P["orange"])
    d.ax.plot([TIMEOUT_X, TIMEOUT_X], [cy - 6, cy + 4], color=P["orange"], lw=2.0, zorder=4)
    d.text(TIMEOUT_X + 1.2, cy + 1, "타임아웃\nSCC → Disabled", size=8.5, color=P["orange"], ha="left")


def draw(d):
    row(d, 36, "활동 상태\n(Recording,\nPlay Back, Abort)", "200 ms", "600 ms")
    row(d, 13, "Ready", "1 s", "3 s")


diagram("54-status-timeout", draw, w=12, h=5.4, xmax=100, ymax=48)

"""CH06 §6 iceConnectionState 상태 머신 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def state(x, y, name, col, w=15, h=7):
        d.box(x - w / 2, y - h / 2, w, h, col)
        d.text(x, y, name, size=10.5, weight="bold")

    state(9, 30, "new", P["gray"])
    state(30, 30, "checking", P["blue"])
    state(53, 30, "connected", P["green"])
    state(78, 30, "completed", P["green"])
    state(53, 10, "disconnected", P["brown"], w=17)
    state(30, 10, "failed", P["purple"])
    state(90, 10, "closed", P["chip"])

    # 정상 흐름
    d.arrow(16.5, 30, 22.5, 30)
    d.text(19.5, 32.2, "원격 후보", size=8, color=P["dim"])
    d.arrow(37.5, 30, 45.5, 30)
    d.text(41.5, 32.2, "쌍 하나 성공", size=8, color=P["dim"])
    d.arrow(60.5, 30, 70.5, 30)
    d.text(65.5, 32.2, "모든 체크 종료", size=8, color=P["dim"])

    # connected <-> disconnected
    d.arrow(51, 26.5, 51, 13.5, color=P["orange"])
    d.text(49.5, 20, "consent/체크 실패", size=8, color=P["orange"], ha="right")
    d.arrow(55, 13.5, 55, 26.5, color=P["accent"])
    d.text(56.5, 20, "스스로 회복", size=8, color=P["accent"], ha="left")
    # completed -> disconnected
    d.arrow(74, 26.5, 61.5, 13.5, color=P["orange"], rad=-0.1)

    # disconnected -> failed
    d.arrow(44.5, 10, 37.5, 10, color=P["orange"])
    d.text(41, 12.2, "회복 실패", size=8, color=P["orange"])
    # checking -> failed
    d.arrow(33, 26.5, 33, 13.5, color=P["orange"])
    d.text(34.5, 20, "모든 쌍 실패", size=8, color=P["orange"], ha="left")

    # failed -> checking (restart)
    d.arrow(25, 13.5, 25, 26.5, color=P["violet"], rad=-0.45)
    d.text(17, 20, "restartIce()\n+ 재협상", size=8, color=P["violet"], ha="center")

    # closed
    d.text(90, 17.5, "close() — 어느 상태에서든", size=8, color=P["dim"])


diagram("06-ice-states", draw, w=12, h=4.8, ymax=40)

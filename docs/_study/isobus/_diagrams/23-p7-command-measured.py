"""CH23 명령은 부탁: 작업기 명령 → 트랙터 판단 → 측정값으로 확인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    # implement
    d.box(3, 13, 27, 20, P["green"])
    d.text(16.5, 25.5, "작업기", size=13, weight="bold")
    d.text(16.5, 19.5, "작업기 ECU · TC", size=9.5, color=P["dim"])

    # tractor
    d.box(60, 6, 37, 33, P["blue"])
    d.text(78.5, 35, "트랙터 (TECU)", size=13, weight="bold")
    d.box(63.5, 9.5, 30, 21, P["chip"])
    d.text(78.5, 27, "실행할지 판단", size=10.5, weight="bold")
    d.text(78.5, 21.5, "운전자 설정 · 조작", size=9.5)
    d.text(78.5, 17.2, "다른 시스템의 명령", size=9.5)
    d.text(78.5, 12.9, "운전 조건", size=9.5)

    # operator
    d.box(66, 43, 25, 6, P["gray"])
    d.text(78.5, 46, "운전자", size=10.5, weight="bold")
    d.arrow(78.5, 43, 78.5, 39.4, color=P["violet"])
    d.text(83.5, 41.2, "캡에서 조작", size=8.5, color=P["violet"], ha="left")

    # command (top) and measured (bottom)
    d.arrow(30.5, 28, 59.5, 28, color=P["orange"], lw=2.2)
    d.text(45, 32.6, "명령 (command)", size=10.5, color=P["orange"], weight="bold")
    d.text(45, 30.0, "후방 히치를 64 %로", size=9, color=P["orange"])

    d.arrow(59.5, 17, 30.5, 17, color=P["accent"], lw=2.2)
    d.text(45, 14.3, "측정값 (measured)", size=10.5, color=P["accent"], weight="bold")
    d.text(45, 11.4, "실제 히치 위치 · 제한 상태", size=9, color=P["accent"])


diagram("23-p7-command-measured", draw, w=12, h=6, xmax=100, ymax=50)

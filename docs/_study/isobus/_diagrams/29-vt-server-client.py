"""CH29 VT Server(트랙터)와 VT Client(작업기 ECU)의 역할 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    d.box(2, 4, 38, 34, P["gray"], lw=1.2)
    d.text(5, 35, "트랙터", size=11, weight="bold", ha="left")
    d.box(60, 4, 38, 34, P["gray"], lw=1.2)
    d.text(63, 35, "작업기", size=11, weight="bold", ha="left")

    d.box(6, 19, 28, 11, P["blue"], ec=P["accent"])
    d.text(20, 24.5, "VT Server\n(CAN 주소 0x26)", size=11)
    d.box(6, 6.5, 28, 7.5, P["chip"])
    d.text(20, 10.25, "디스플레이 하드웨어", size=10.5)
    d.arrow(20, 19, 20, 14.2, color=P["dim"])

    d.box(66, 19, 28, 11, P["green"], ec=P["accent"])
    d.text(80, 24.5, "작업기 ECU\n(VT Client)", size=11)

    d.arrow(66, 27.2, 34, 27.2, color=P["accent"])
    d.text(50, 29.2, "오브젝트 풀 전송", size=9.5, color=P["accent"])
    d.arrow(34, 21.8, 66, 21.8, color=P["orange"])
    d.text(50, 19.6, "사용자 입력 이벤트", size=9.5, color=P["orange"])


diagram("29-vt-server-client", draw, w=11, h=4.6, xmax=100, ymax=40)

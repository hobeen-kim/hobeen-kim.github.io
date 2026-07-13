"""CH18 Looper/Handler/MessageQueue — 메인 스레드 이벤트 루프 구조."""
from _common import diagram


def draw(d):
    P = d.P

    # 메인 스레드 그룹
    d.box(4, 6, 58, 38, P["gray"], ec=P["accent"], lw=1.6)
    d.text(33, 40.5, "메인 스레드 (Looper.loop)", size=10.5, weight="bold",
           color=P["accent"])

    # MessageQueue
    d.box(8, 14, 22, 22, P["brown"])
    d.text(19, 33.5, "MessageQueue", size=9.5, weight="bold")
    for i, m in enumerate(["Message", "Message", "Message"]):
        d.box(11, 27 - i * 5, 16, 4, P["blue"])
        d.text(19, 29 - i * 5, m, size=8)
    d.text(19, 11.5, "when 순 정렬 · 배리어", size=7.4, color=P["dim"])

    # Looper 루프
    d.box(38, 20, 20, 14, P["green"])
    d.text(48, 30.5, "Looper", size=9.5, weight="bold")
    d.text(48, 26.5, "next() → dispatch", size=8)
    d.text(48, 23, "비면 epoll_wait\n(블록, CPU 0%)", size=7.6, color=P["dim"])

    d.arrow(30, 27, 38, 27, color=P["orange"])
    d.text(34, 28.4, "꺼냄", size=7.2, color=P["orange"])

    # Handler (우측)
    d.box(70, 26, 24, 10, P["purple"])
    d.text(82, 32.5, "Handler", size=9.5, weight="bold")
    d.text(82, 29, "post() · sendMessage()", size=7.8)
    d.arrow(70, 30, 30, 30, color=P["violet"], rad=-0.15)
    d.text(52, 37, "enqueue", size=7.4, color=P["violet"])

    # 입력 소스
    d.box(70, 10, 24, 12, P["chip"])
    d.text(82, 19.5, "입력 소스", size=9, weight="bold", color=P["dim"])
    d.text(82, 15, "터치·센서 fd\nVSYNC (Choreographer)\nBinder 콜백", size=7.8)
    d.arrow(70, 16, 58, 24, color=P["edge"], lw=1.2, rad=0.1)


diagram("18-looper", draw, w=12.5, h=5.8, ymax=46)

"""CH17 §2 스레드 구조 — 수신 스레드가 Rx 큐를 채우고, 주기 스레드가 3단계로 처리한다."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽: 하드웨어
    d.box(2, 16, 14, 18, P["gray"], ec=P["accent"], lw=1.5)
    d.text(9, 25, "CAN 하드웨어\n(소켓 · 컨트롤러)", size=10)

    # 수신 스레드
    d.box(20, 33, 24, 9, P["brown"])
    d.text(32, 39.3, "수신 스레드", size=10.5, weight="bold")
    d.text(32, 36, "read_frame() 반복", size=9, color=P["dim"])

    d.arrow(16, 30, 22, 33, color=P["orange"], rad=0.15)

    # Rx 큐
    d.box(50, 33, 14, 9, P["chip"])
    d.text(57, 37.5, "Rx 큐", size=10.5)
    d.arrow(44, 37.5, 50, 37.5, color=P["orange"])

    # 주기 스레드 그룹
    d.box(20, 6, 60, 22, P["blue"], alpha=0.35, ec=P["edge"])
    d.text(50, 25.5, "주기 스레드 (기본 4 ms 간격 · update())", size=10.5, weight="bold")

    steps = [
        ("1. Rx 큐 비우기", "네트워크 매니저가\n메시지 처리 · 콜백 호출"),
        ("2. 프로토콜 갱신", "주소 클레임 · TP/ETP\n· VT/TC 클라이언트"),
        ("3. Tx 큐 송신", "실패할 때까지\nwrite_frame() 반복"),
    ]
    x = 23
    for title, body in steps:
        d.box(x, 9, 17, 13, P["chip"])
        d.text(x + 8.5, 19, title, size=9.8, weight="bold")
        d.text(x + 8.5, 14.5, body, size=8.8, color=P["dim"])
        x += 19

    d.arrow(40, 15.5, 42, 15.5, color=P["accent"])
    d.arrow(59, 15.5, 61, 15.5, color=P["accent"])

    # 큐 연결
    d.arrow(56, 33, 31.5, 22, color=P["orange"], rad=0.18)

    # Tx 큐
    d.box(84, 20, 14, 9, P["chip"])
    d.text(91, 24.5, "Tx 큐", size=10.5)
    d.arrow(78, 15.5, 84, 21.5, color=P["violet"])

    # Tx 큐 → 하드웨어 (아래로 우회)
    d.arrow(91, 20, 91, 2.5, color=P["violet"], style="-", lw=1.5)
    d.arrow(91, 2.5, 9, 2.5, color=P["violet"], style="-", lw=1.5)
    d.arrow(9, 2.5, 9, 16, color=P["violet"], lw=1.5)

    # 애플리케이션 송신 진입
    d.box(84, 33, 14, 9, P["green"])
    d.text(91, 37.5, "애플리케이션\nsend_*()", size=9.2)
    d.arrow(91, 33, 91, 29, color=P["violet"])


diagram("17-plugin-threads", draw, w=13, h=6.2, ymax=45)

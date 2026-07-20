"""CH10 §1 send_can_message 한 번 호출에서 스택이 프로토콜을 고르는 순서."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 18, 22, 12, P["blue"])
    d.text(13, 26, "send_can_message(...)", size=9.6)
    d.text(13, 21.5, "dataLength", size=9, color=P["dim"])

    # 1차 시도: TP
    d.box(30, 30, 30, 13, P["green"])
    d.text(45, 38.5, "TransportProtocolManager", size=9.4)
    d.text(45, 34, "9 ~ 1785 byte\nBAM(브로드캐스트) / CMDT(목적지)", size=8.8, color=P["dim"])

    # 2차 시도: ETP
    d.box(30, 15, 30, 12, P["purple"])
    d.text(45, 23, "ExtendedTransportProtocolManager", size=9.2)
    d.text(45, 18.5, "1786 ~ 117,440,505 byte\n목적지 지정 전용", size=8.8, color=P["dim"])

    # 최종: 단일 프레임
    d.box(30, 2, 30, 10, P["gray"])
    d.text(45, 7, "send_can_message_raw\n1 ~ 8 byte 단일 프레임", size=9, color=P["dim"])

    d.arrow(24, 26, 30, 36, color=P["accent"])
    d.text(27.5, 33, "①", size=9, color=P["dim"])
    d.arrow(45, 30, 45, 27, color=P["orange"], rad=0.0)
    d.text(49.5, 28.6, "② 거절 시", size=8.4, color=P["dim"], ha="left")
    d.arrow(45, 15, 45, 12, color=P["orange"])
    d.text(49.5, 13.6, "③ 거절 시", size=8.4, color=P["dim"], ha="left")

    # 결과
    d.box(70, 30, 28, 13, P["chip"])
    d.text(84, 36.5, "여러 프레임으로 분할 송신\n수신 측은 재조립 후 콜백 1회", size=9, color=P["dim"])
    d.box(70, 2, 28, 10, P["chip"])
    d.text(84, 7, "프레임 1개 그대로 송신", size=9, color=P["dim"])

    d.arrow(60, 36.5, 70, 36.5, color=P["violet"])
    d.arrow(60, 21, 70, 33, color=P["violet"])
    d.arrow(60, 7, 70, 7, color=P["violet"])


diagram("10-protocol-selection", draw, w=13, h=5.6, ymax=46)

"""CH9 §3 송신 두 경로 — 브로드캐스트 vs 목적지 지정 (인자 하나 차이)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 16, 24, 12, P["blue"])
    d.text(14, 22, "myECU\n(InternalControlFunction)", size=9.5)

    # 브로드캐스트 경로
    d.box(34, 27, 36, 11, P["green"])
    d.text(52, 34.5, "send_can_message(pgn, data, len, myECU)", size=9.2)
    d.text(52, 30, "PDU2 / DA = 0xFF (Global)", size=9, color=P["dim"])
    d.arrow(26, 25, 34, 32.5, color=P["orange"])

    # 목적지 지정 경로
    d.box(34, 6, 36, 11, P["purple"])
    d.text(52, 13.5, "send_can_message(pgn, data, len,\nmyECU, myPartner)", size=9.2)
    d.text(52, 8.6, "PDU1 / DA = 파트너 주소", size=9, color=P["dim"])
    d.arrow(26, 19, 34, 11.5, color=P["violet"])

    # 수신측
    d.box(78, 27, 20, 11, P["chip"])
    d.text(88, 32.5, "버스의 모든 CF", size=9.5, color=P["dim"])
    d.box(78, 6, 20, 11, P["chip"])
    d.text(88, 11.5, "파트너 CF 하나", size=9.5, color=P["dim"])

    d.arrow(70, 32.5, 78, 32.5, color=P["orange"])
    d.arrow(70, 11.5, 78, 11.5, color=P["violet"])


diagram("09-send-paths", draw, w=12.5, h=4.8, ymax=42)

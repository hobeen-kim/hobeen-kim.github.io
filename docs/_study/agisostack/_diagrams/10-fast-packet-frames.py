"""CH10 §3 Fast Packet 프레임 구성 — 첫 프레임 6바이트, 후속 프레임 7바이트."""
from _common import diagram


def draw(d):
    P = d.P

    y = 15
    # 첫 프레임
    d.box(3, y, 30, 11, P["blue"])
    d.text(18, y + 8.4, "프레임 0", size=9.4)
    d.box(5, y + 1.6, 5.5, 4.6, P["chip"])
    d.text(7.75, y + 3.9, "SEQ\n+FRM", size=7.4, color=P["dim"])
    d.box(11.2, y + 1.6, 5.5, 4.6, P["chip"])
    d.text(13.95, y + 3.9, "총\n길이", size=7.4, color=P["dim"])
    d.box(17.4, y + 1.6, 13.6, 4.6, P["green"])
    d.text(24.2, y + 3.9, "데이터 6 byte", size=8.4, color=P["dim"])

    # 후속 프레임
    d.box(38, y, 30, 11, P["purple"])
    d.text(53, y + 8.4, "프레임 1 ~ 31", size=9.4)
    d.box(40, y + 1.6, 5.5, 4.6, P["chip"])
    d.text(42.75, y + 3.9, "SEQ\n+FRM", size=7.4, color=P["dim"])
    d.box(46.2, y + 1.6, 19.8, 4.6, P["green"])
    d.text(56.1, y + 3.9, "데이터 7 byte", size=8.4, color=P["dim"])

    d.arrow(33, y + 4, 38, y + 4, color=P["accent"])

    d.box(73, y, 25, 11, P["chip"])
    d.text(85.5, y + 5.5, "최대 6 + 31 x 7\n= 223 byte", size=9.2, color=P["dim"])
    d.arrow(68, y + 5.5, 73, y + 5.5, color=P["violet"])

    # 프레임마다 PGN 유지
    d.box(3, 2, 95, 9, P["gray"])
    d.text(50.5, 8.0, "모든 프레임이 같은 PGN·우선순위를 그대로 유지한다 (TP.CM·TP.DT 같은 별도 PGN이 없다)", size=9.2, color=P["dim"])
    d.text(50.5, 4.6, "→ 수신 측이 register_multipacket_message_callback 으로 명시 등록해야 재조립된다",
           size=9, color=P["dim"])


diagram("10-fast-packet-frames", draw, w=13, h=3.9, ymax=28)

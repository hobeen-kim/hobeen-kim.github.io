"""CH05 §1 NAT가 P2P를 막는 이유 — LTE 이중 NAT 로봇과 사무실 NAT 운영자 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # LTE side (double NAT)
    d.box(1, 3, 35, 44, P["gray"], ec=P["edge"], lw=1.2)
    d.text(3, 44.5, "LTE 망 (이중 NAT)", size=9.5, color=P["accent"], ha="left")
    d.box(6, 33, 25, 8, P["green"])
    d.text(18.5, 37, "로봇·농기계\n(192.168.8.10)", size=9)
    d.box(6, 20, 25, 8, P["brown"])
    d.text(18.5, 24, "LTE 라우터 NAT\n(WAN 100.64.12.34)", size=9)
    d.box(6, 7, 25, 8, P["brown"], ec=P["accent"], lw=1.6)
    d.text(18.5, 11, "통신사 CGN\n(공인 203.0.113.7)", size=9)
    d.arrow(18.5, 33, 18.5, 28)
    d.arrow(18.5, 20, 18.5, 15)

    # office side
    d.box(64, 3, 35, 44, P["gray"], ec=P["edge"], lw=1.2)
    d.text(66, 44.5, "사무실 망", size=9.5, color=P["accent"], ha="left")
    d.box(69, 30, 25, 8, P["blue"])
    d.text(81.5, 34, "운영자 PC\n(192.168.0.10)", size=9)
    d.box(69, 12, 25, 8, P["brown"], ec=P["accent"], lw=1.6)
    d.text(81.5, 16, "공유기 NAT\n(공인 198.51.100.20)", size=9)
    d.arrow(81.5, 30, 81.5, 20)

    # STUN server on the public internet
    d.box(40, 36, 20, 8, P["chip"], ec=P["accent"], lw=1.4)
    d.text(50, 40, "STUN 서버\n(공인 주소)", size=9)
    d.text(50, 30.5, "인터넷", size=10, color=P["dim"])

    # outbound passes
    d.arrow(31, 13, 42, 36, color=P["accent"])
    d.text(37.5, 19, "outbound\n통과", size=8.5, color=P["accent"], ha="left")
    d.arrow(69, 18, 58, 36, color=P["accent"])
    d.text(62, 23.5, "outbound\n통과", size=8.5, color=P["accent"], ha="right")

    # unsolicited inbound dropped
    d.arrow(69, 14, 31.5, 9.5, color=P["orange"], ls="--")
    d.text(50, 11.7, "X", size=17, color=P["orange"], weight="bold")
    d.text(50, 6.5, "요청한 적 없는 inbound → 폐기", size=8.5, color=P["orange"])


diagram("05-nat-topology", draw, w=12, h=6, ymax=48)

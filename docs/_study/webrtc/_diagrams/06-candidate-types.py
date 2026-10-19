"""CH06 §1 ICE 후보 네 종류 — host/srflx/relay/prflx가 어디서 생기는가 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # LAN 그룹
    d.box(2, 7, 30, 30, P["gray"], ec=P["edge"], lw=1.2)
    d.text(4, 34.5, "농기계 LAN", size=9.5, color=P["dim"], ha="left")

    d.box(5, 17, 24, 9, P["green"])
    d.text(17, 21.5, "디바이스 ICE 에이전트\n(192.168.0.10:46243)", size=9.5)
    d.text(17, 12.5, "host = 자기 NIC 주소", size=8.5, color=P["accent"])

    # NAT
    d.box(37, 15, 12, 13, P["brown"])
    d.text(43, 21.5, "NAT 라우터\n(203.0.113.5)", size=9.5)
    d.arrow(29, 21.5, 37, 21.5, color=P["edge"])

    # 오른쪽 열: STUN / TURN / 상대 피어
    d.box(57, 31, 18, 7, P["blue"])
    d.text(66, 34.5, "STUN 서버", size=9.5)
    d.box(57, 18, 18, 8, P["purple"])
    d.text(66, 22, "TURN 서버\n(198.51.100.20)", size=9.5)
    d.box(57, 4, 18, 8, P["chip"])
    d.text(66, 8, "상대 피어\n(브라우저)", size=9.5)

    # srflx
    d.arrow(49, 26, 57, 33.5, color=P["orange"])
    d.text(49.5, 31.5, "Binding", size=8, color=P["orange"], ha="left")
    d.text(77, 34.5, "srflx = NAT가 바꾼 공인 주소\n(203.0.113.5:61722)",
           size=8.5, color=P["orange"], ha="left")

    # relay
    d.arrow(49, 22, 57, 22, color=P["violet"])
    d.text(53, 23.5, "Allocate", size=8, color=P["violet"])
    d.text(77, 22, "relay = TURN이 빌려준 주소\n(198.51.100.20:50112)",
           size=8.5, color=P["violet"], ha="left")

    # prflx
    d.arrow(49, 17, 57, 9, color=P["accent"], ls="--")
    d.text(50, 11, "check", size=8, color=P["accent"], ha="left")
    d.text(77, 8, "prflx = connectivity check\n도중 처음 보는 주소로 발견",
           size=8.5, color=P["accent"], ha="left")


diagram("06-candidate-types", draw, w=12.5, h=5.2, ymax=41)

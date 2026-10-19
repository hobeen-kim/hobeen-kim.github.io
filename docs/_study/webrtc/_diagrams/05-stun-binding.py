"""CH05 §4 STUN Binding 흐름 — 요청·NAT 재작성·XOR-MAPPED-ADDRESS 응답 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    actors = [
        (12, "클라이언트\n(10.0.0.2:5000)", P["green"]),
        (50, "NAT\n(공인 203.0.113.7)", P["brown"]),
        (88, "STUN 서버\n(198.51.100.1:3478)", P["blue"]),
    ]
    for x, name, col in actors:
        d.box(x - 10.5, 47, 21, 6.5, col)
        d.text(x, 50.25, name, size=9.2)
        d.ax.plot([x, x], [2, 47], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color):
        d.arrow(x1, y, x2, y, color=color)
        d.text((x1 + x2) / 2, y + 2.2, label, size=8.4, color=color)

    hop(12, 50, 40, "Binding Request · TID=t1\nsrc 10.0.0.2:5000", P["accent"])
    hop(50, 88, 33, "src를 203.0.113.7:40001로 재작성\n(IP/UDP 헤더만 바꿈)", P["accent"])

    d.box(73, 23.5, 30 - 4, 4.4, P["chip"], lw=1.0)
    d.text(86, 25.7, "보이는 출발지 = 203.0.113.7:40001", size=8.3)

    hop(88, 50, 17.5, "Binding Success · TID=t1\nXOR-MAPPED-ADDRESS = 주소 ⊕ 쿠키", P["orange"])
    d.text(69, 13.6, "중간 ALG가 공인 IP 바이트열을 찾아도 매칭 안 됨", size=8,
           color=P["dim"])
    hop(50, 12, 8.5, "dst만 10.0.0.2:5000으로 되돌림\n(페이로드는 그대로)", P["orange"])

    d.box(1, 1.2, 26, 4.4, P["chip"], ec=P["accent"], lw=1.0)
    d.text(14, 3.4, "XOR 복원 → srflx 203.0.113.7:40001", size=8.3)


diagram("05-stun-binding", draw, w=12.5, h=7, ymax=55)

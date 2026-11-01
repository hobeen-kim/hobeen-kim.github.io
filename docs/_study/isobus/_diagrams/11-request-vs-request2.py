"""CH11 §1 Request와 Request2·Transfer 응답 비교: 주인 표시가 붙는가 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(x, y, w, h, label, fc, size=9.0, ec=None):
        d.box(x, y, w, h, fc, ec=ec)
        d.text(x + w / 2, y + h / 2, label, size=size)

    # 행 1: Request
    node(1, 36, 12, 8, "VT\nSA 0x26", P["blue"])
    d.arrow(13, 40, 27, 40)
    d.text(20, 43.6, "Request\nPGN 65242", size=8.2)
    node(27, 36, 16, 8, "작업기 ECU\nSA 0x80", P["green"])
    d.arrow(43, 40, 51, 40)
    node(51, 36, 49, 8, "SW1.0* 하나만\nECU 자기 데이터, 주인 표시 없음", P["chip"], size=8.8)

    # 행 2: Request2 + Transfer
    node(1, 14, 12, 8, "VT\nSA 0x26", P["blue"])
    d.arrow(13, 18, 27, 18)
    d.text(20, 21.6, "Request2\nTransfer = Yes", size=8.2)
    node(27, 14, 16, 8, "작업기 ECU\nSA 0x80", P["green"])
    node(27, 1.5, 16, 7, "맡은 CF", P["gray"], size=8.6)
    d.ax.plot([35, 35], [8.5, 14], color=P["edge"], lw=1.2, ls=(0, (2, 2)))
    d.arrow(43, 18, 51, 18)

    segs = [  # (폭, 라벨, 색)
        (8, "PGN\n65242", "purple"),
        (4, "길이\n11", "brown"),
        (9.5, "신원\nECU", "blue"),
        (7, "SW1.0*", "green"),
        (4, "길이\n11", "brown"),
        (9.5, "신원\n맡은 CF", "blue"),
        (7, "SW2.3*", "green"),
    ]
    x = 51
    edges = [x]
    for w, label, color in segs:
        d.box(x, 14, w, 8, P[color], r=0.01)
        d.text(x + w / 2, 18, label, size=7.8)
        x += w
        edges.append(x)
    d.text((51 + x) / 2, 24.4, "Transfer (PGN 51712)", size=8.6, color=P["dim"])

    for a, b, s in ((edges[1], edges[4], "세트 1 (ECU 자신)"),
                    (edges[4], edges[7], "세트 2 (맡은 CF)")):
        d.ax.plot([a + 0.4, a + 0.4, b - 0.4, b - 0.4], [12.2, 11.2, 11.2, 12.2],
                  color=P["accent"], lw=1.3)
        d.text((a + b) / 2, 8.8, s, size=8.2, color=P["accent"])


diagram("11-request-vs-request2", draw, w=12, h=4.8, xmax=101, ymax=48)

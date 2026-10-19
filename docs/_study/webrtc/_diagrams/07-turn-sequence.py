"""CH07 §2 TURN 메시지 흐름 — Allocate 401 → 인증 → 할당 → 권한 → 채널 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    actors = [
        (12, "TURN 클라이언트\n(디바이스 ICE 에이전트)", P["green"]),
        (55, "TURN 서버\n(relay 198.51.100.20:50112)", P["purple"]),
        (87, "상대 피어\n(203.0.113.77)", P["blue"]),
    ]
    for x, name, col in actors:
        d.box(x - 11, 73, 22, 7, col)
        d.text(x, 76.5, name, size=9.2, weight="bold")
        d.ax.plot([x, x], [2, 73], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        d.text((x1 + x2) / 2, y + 1.3, label, size=8, color=color)

    # 1) 인증 + 할당
    d.box(2, 50, 64, 21.5, P["chip"], ec=P["accent"], lw=1.0)
    d.text(3.5, 70, "할당 (long-term credential)", size=8.3,
           color=P["accent"], ha="left", style="italic")
    hop(12, 55, 66, "Allocate  REQUESTED-TRANSPORT=UDP", P["accent"])
    hop(55, 12, 62, "401 Unauthorized  REALM · NONCE", P["orange"], ls="--")
    hop(12, 55, 57.5, "Allocate + USERNAME · REALM · NONCE · MESSAGE-INTEGRITY",
        P["accent"])
    hop(55, 12, 52.5, "성공  XOR-RELAYED-ADDRESS · XOR-MAPPED-ADDRESS · LIFETIME=600",
        P["dim"], ls="--")

    # 2) 권한 + indication
    d.box(2, 27, 96, 21.5, P["chip"], ec=P["violet"], lw=1.0)
    d.text(3.5, 47, "권한과 Send/Data indication", size=8.3,
           color=P["violet"], ha="left", style="italic")
    hop(12, 55, 43, "CreatePermission  XOR-PEER-ADDRESS=203.0.113.77", P["violet"])
    hop(55, 12, 39, "성공 (권한 300초)", P["dim"], ls="--")
    hop(12, 55, 34.5, "Send indication (+36B 헤더)", P["violet"])
    hop(55, 87, 34.5, "UDP (relay 주소에서)", P["dim"])
    hop(87, 55, 29.5, "UDP", P["dim"])
    hop(55, 12, 29.5, "Data indication", P["violet"])

    # 3) 채널
    d.box(2, 4, 96, 21, P["chip"], ec=P["orange"], lw=1.0)
    d.text(3.5, 23.5, "채널 (오버헤드 최소화)", size=8.3,
           color=P["orange"], ha="left", style="italic")
    hop(12, 55, 19.5, "ChannelBind  CHANNEL-NUMBER=0x4000", P["orange"])
    hop(55, 12, 15.5, "성공 (채널 600초)", P["dim"], ls="--")
    hop(12, 55, 11, "ChannelData 0x4000 (+4B 헤더)", P["orange"])
    hop(55, 87, 11, "UDP", P["dim"])
    hop(87, 55, 6.5, "UDP", P["dim"])
    hop(55, 12, 6.5, "ChannelData 0x4000", P["orange"])

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.0, label="요청 / indication"),
        Line2D([0], [0], color=P["dim"], lw=2.0, ls="--", label="응답"),
    ], loc="lower right", anchor=(0.995, -0.01))


diagram("07-turn-sequence", draw, w=12.5, h=9.0, ymax=81)

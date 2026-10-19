"""CH06 §3 connectivity check와 정규 nomination 시퀀스 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    actors = [
        (12, "브라우저 (offerer)\ncontrolling", P["blue"]),
        (50, "시그널링 서버", P["gray"]),
        (88, "디바이스 (answerer)\ncontrolled", P["green"]),
    ]
    for x, name, col in actors:
        d.box(x - 10, 55, 20, 7, col)
        d.text(x, 58.5, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [3, 55], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", dy=1.3):
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        d.text((x1 + x2) / 2, y + dy, label, size=8, color=color)

    # 시그널링 경유 (trickle)
    hop(12, 50, 51, "offer (ufrag/pwd)", P["dim"], ls="--")
    hop(50, 88, 51, "", P["dim"], ls="--")
    hop(88, 50, 47, "answer", P["dim"], ls="--")
    hop(50, 12, 47, "", P["dim"], ls="--")
    hop(12, 50, 43, "candidate (trickle)", P["dim"], ls="--")
    hop(50, 88, 43, "", P["dim"], ls="--")
    hop(88, 50, 39, "candidate (trickle)", P["dim"], ls="--")
    hop(50, 12, 39, "", P["dim"], ls="--")

    # 직접 경로 체크 구간
    d.box(3, 5, 94, 31, P["chip"], ec=P["accent"], lw=1.1)
    d.text(5, 34, "후보 쌍 위에서 직접 (STUN Binding)", size=8.5,
           color=P["accent"], ha="left", style="italic")

    hop(12, 88, 29.5, "Binding 요청  USERNAME=R:L · PRIORITY · ICE-CONTROLLING",
        P["accent"])
    hop(88, 12, 25.5, "Binding 성공 응답 (XOR-MAPPED-ADDRESS)", P["accent"], ls="-")
    hop(88, 12, 21, "triggered check  ICE-CONTROLLED", P["orange"])
    hop(12, 88, 17, "성공 응답", P["orange"], ls="-")
    d.text(50, 13.2, "양방향 성공 → 이 쌍은 valid", size=8, color=P["dim"])
    hop(12, 88, 8.5, "Binding 요청 + USE-CANDIDATE  (nomination)", P["violet"])
    d.text(50, 5.9, "성공하면 양쪽이 nominated → selected pair", size=8,
           color=P["violet"])

    d.legend([
        Line2D([0], [0], color=P["dim"], lw=2.0, ls="--", label="시그널링 경유"),
        Line2D([0], [0], color=P["accent"], lw=2.0, label="직접 경로"),
    ], loc="lower left", anchor=(0.0, -0.01))


diagram("06-connectivity-check", draw, w=12.5, h=7.4, ymax=63)

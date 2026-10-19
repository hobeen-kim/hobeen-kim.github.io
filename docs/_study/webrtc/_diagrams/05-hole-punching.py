"""CH05 §5 UDP 홀펀칭 — 양쪽이 서로의 srflx로 보내며 NAT 규칙을 여는 순서 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    actors = [
        (8, "피어 A\n(로봇)", P["green"]),
        (34, "NAT A\n(203.0.113.7)", P["brown"]),
        (66, "NAT B\n(198.51.100.20)", P["brown"]),
        (92, "피어 B\n(운영자)", P["blue"]),
    ]
    for x, name, col in actors:
        d.box(x - 7.5, 46, 15, 6.5, col)
        d.text(x, 49.25, name, size=9)
        d.ax.plot([x, x], [3, 46], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    d.box(2, 38.5, 96, 4.4, P["chip"], ec=P["accent"], lw=1.0)
    d.text(50, 40.7, "준비: STUN으로 각자 srflx 확인 → 시그널링으로 후보 교환",
           size=8.8, color=P["accent"])

    # 1: A -> B srflx, dropped at NAT B
    d.arrow(8, 32, 65, 32, color=P["orange"])
    d.text(36, 33.7, "① A → B의 srflx : NAT A에 'B로 보냄' 기록", size=8.6,
           color=P["orange"])
    d.text(66, 32, "X", size=16, color=P["orange"], weight="bold")
    d.text(68.5, 29.2, "B가 먼저 보낸 적 없음 → 폐기", size=8.2,
           color=P["orange"], ha="left")

    # 2: B -> A srflx, passes NAT A thanks to step 1
    d.arrow(92, 23, 8, 23, color=P["accent"])
    d.text(50, 24.7, "② B → A의 srflx : NAT B에 기록, NAT A는 ①의 기록 덕에 통과",
           size=8.6, color=P["accent"])

    # 3: A -> B again, passes NAT B thanks to step 2
    d.arrow(8, 15, 92, 15, color=P["accent"])
    d.text(50, 16.7, "③ A → B 재전송 : 이제 NAT B도 통과", size=8.6,
           color=P["accent"])

    # 4: bidirectional path
    d.arrow(8, 7, 92, 7, color=P["violet"], style="<|-|>", lw=2.6)
    d.text(50, 8.9, "양방향 UDP 경로 확보 (ICE connectivity check 성공)",
           size=8.6, color=P["violet"])


diagram("05-hole-punching", draw, w=12.5, h=6.6, ymax=53)

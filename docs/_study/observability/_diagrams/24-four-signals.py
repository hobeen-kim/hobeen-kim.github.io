"""CH24 관측성 4대 신호 — 4번째 신호로서의 프로파일 (light/dark PNG)."""
from _common import diagram
from _common import Line2D


def draw(d):
    P = d.P

    # 허브
    d.box(37, 40, 26, 6, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 43, "관측성 4대 신호", size=12, weight="bold", color=P["accent"])

    signals = [
        (14, "메트릭", "무엇이 얼마나", P["blue"], P["edge"]),
        (38, "로그", "무슨 일이 있었나", P["brown"], P["edge"]),
        (62, "트레이스", "서비스·스팬 단위\n어디서 시간을 썼나", P["green"], P["edge"]),
        (86, "프로파일", "함수·라인 단위\n어디서 시간을 썼나", P["purple"], P["accent"]),
    ]
    for x, t, sub, c, ec in signals:
        lw = 1.9 if t == "프로파일" else 1.4
        d.box(x - 11, 16, 22, 12, c, ec=ec, lw=lw)
        d.text(x, 24.5, t, size=12, weight="bold")
        d.text(x, 20.3, sub, size=8.5, color=P["dim"])
        d.arrow(50, 40, x, 28.2, color=P["edge"], lw=1.6)

    d.text(86, 30, "4번째 신호", size=8, color=P["violet"],
           weight="bold", style="italic")

    # span profiles: 트레이스 → 프로파일
    d.arrow(68, 16, 80, 16, color=P["orange"], lw=2.0,
            ls=(0, (5, 3)), rad=-0.5)
    d.text(74, 10.5, "span profiles", size=9, color=P["orange"], weight="bold")

    leg = [
        Line2D([0], [0], color=P["edge"], lw=2.0, label="4대 신호 구성"),
        Line2D([0], [0], color=P["orange"], lw=2.0, ls="--",
               label="span profiles (트레이스↔프로파일)"),
    ]
    d.legend(leg, anchor=(0.005, 0.02))


diagram("24-four-signals", draw, w=13, h=7, ymax=50)

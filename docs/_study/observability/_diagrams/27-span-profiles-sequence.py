"""CH27 span profiles — 트레이스↔프로파일 연계 시퀀스 (light/dark PNG)."""
from _common import diagram
from _common import Line2D


def draw(d):
    P = d.P

    lanes = [
        (20, "OTel SDK", "트레이싱", P["green"]),
        (50, "애플리케이션 코드", "비즈니스 로직", P["blue"]),
        (80, "Pyroscope SDK", "프로파일링", P["brown"]),
    ]
    for x, t, sub, c in lanes:
        d.box(x - 11, 44, 22, 5, c)
        d.text(x, 47.4, t, size=11, weight="bold")
        d.text(x, 45.2, sub, size=8, color=P["dim"])
        d.ax.plot([x, x], [6, 44], color=P["edge"], lw=1.1,
                  ls=(0, (4, 3)), zorder=1)

    # span 시작
    d.arrow(20, 39, 50, 39, color=P["accent"], lw=2.0)
    d.text(35, 40.6, "span 시작 (span_id=abc123)", size=8.5, color=P["accent"])

    # span 활성 구간
    d.box(9, 16, 82, 19, P["chip"], ec=P["orange"], lw=1.4)
    d.text(14, 33, "span 활성 구간", size=9.5, color=P["orange"], weight="bold", ha="left")

    # 태그 부착
    d.arrow(50, 29, 80, 29, color=P["orange"], lw=2.0)
    d.text(65, 31, "샘플에 span_id 태그 부착", size=8.5, color=P["orange"])

    # 비즈니스 로직
    d.box(38, 21, 24, 4.4, P["blue"])
    d.text(50, 23.2, "비즈니스 로직 실행", size=9)
    d.arrow(50, 29, 50, 25.4, color=P["dim"], lw=1.6)

    # note
    d.box(64, 17.5, 24, 4.2, P["brown"], ec=P["brown"])
    d.text(76, 19.6, "이 구간 샘플만 span_id로 필터", size=8, color=P["dim"])

    # span 종료
    d.arrow(20, 12, 50, 12, color=P["accent"], lw=2.0)
    d.text(35, 13.6, "span 종료", size=8.5, color=P["accent"])

    leg = [
        Line2D([0], [0], color=P["accent"], lw=2.2, label="span 시작·종료 (OTel)"),
        Line2D([0], [0], color=P["orange"], lw=2.2, label="span_id 태그 부착 (Pyroscope)"),
    ]
    d.legend(leg, anchor=(0.005, 0.02))


diagram("27-span-profiles-sequence", draw, w=13, h=6.2, ymax=52)

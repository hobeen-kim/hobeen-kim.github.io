"""CH24 샘플링 기반 프로파일링 — 타이머 인터럽트 시퀀스 (light/dark PNG)."""
from _common import diagram
from _common import Line2D


def draw(d):
    P = d.P

    lanes = [
        (20, "샘플링 타이머", "예: 100Hz", P["brown"]),
        (50, "애플리케이션 런타임", "실행 중 프로세스", P["blue"]),
        (80, "프로파일러", "스택 집계기", P["green"]),
    ]
    for x, t, sub, c in lanes:
        d.box(x - 10, 40, 20, 5.5, c)
        d.text(x, 43.4, t, size=11, weight="bold")
        d.text(x, 41.2, sub, size=8, color=P["dim"])
        d.ax.plot([x, x], [6, 40], color=P["edge"], lw=1.1,
                  ls=(0, (4, 3)), zorder=1)

    # loop 박스
    d.box(9, 14, 82, 22, P["chip"], ec=P["accent"], lw=1.5)
    d.text(15.5, 34, "loop  10ms 마다", size=9.5, color=P["accent"],
           weight="bold", ha="left")

    # 인터럽트
    d.arrow(20, 29, 50, 29, color=P["orange"], lw=2.0)
    d.text(35, 30.6, "인터럽트 발생", size=8, color=P["orange"])

    # 콜 스택 캡처
    d.arrow(50, 23, 80, 23, color=P["accent"], lw=1.8, ls=(0, (5, 3)))
    d.text(65, 24.6, "현재 콜 스택 캡처", size=8, color=P["accent"])

    # 카운트 누적
    d.box(63, 15.5, 20, 4.2, P["green"])
    d.text(73, 17.6, "동일 스택 카운트 누적", size=8)
    d.arrow(80, 21, 80, 19.7, color=P["violet"], lw=1.8)

    # 집계
    d.box(58, 4.5, 38, 5.5, P["green"], ec=P["accent"], lw=1.5)
    d.text(77, 7.2, "스택별 빈도 집계 → 프로파일 생성", size=9.5, weight="bold")
    d.arrow(80, 14, 80, 10, color=P["green"], lw=2.0)

    leg = [
        Line2D([0], [0], color=P["orange"], lw=2.2, label="타이머 인터럽트"),
        Line2D([0], [0], color=P["accent"], lw=2.2, ls="--", label="콜 스택 캡처"),
        Line2D([0], [0], color=P["violet"], lw=2.2, label="카운트 누적"),
    ]
    d.legend(leg, anchor=(0.005, 0.02))


diagram("24-sampling-sequence", draw, w=12, h=6.2, ymax=48)

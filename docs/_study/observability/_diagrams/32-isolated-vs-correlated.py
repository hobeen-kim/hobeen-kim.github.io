"""CH32 신호 고립 vs 상관관계 연결 비교 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ===== 위: 고립 =====
    d.box(4, 27, 92, 13, P["brown"], ec=P["orange"], lw=1.6)
    d.text(9, 38, "신호가 고립된 경우", size=12, weight="bold", color=P["orange"], ha="left")
    iso = [(20, "메트릭 이상 발견"), (52, "로그 확인"), (84, "트레이스 조회")]
    for x, t in iso:
        d.box(x - 9, 29.5, 18, 5, P["chip"])
        d.text(x, 32, t, size=10)
    d.arrow(29, 32, 43, 32, color=P["orange"], lw=1.9)
    d.text(36, 34.2, "수동으로 시간·서비스\n맞춰 검색", size=8, color=P["orange"])
    d.arrow(61, 32, 75, 32, color=P["orange"], lw=1.9)
    d.text(68, 34.2, "수동으로\ntrace ID 복사", size=8, color=P["orange"])

    # ===== 아래: 상관관계 연결 =====
    d.box(4, 4, 92, 18.5, P["green"], ec=P["accent"], lw=1.8)
    d.text(9, 21, "상관관계가 연결된 경우", size=12, weight="bold", color=P["accent"], ha="left")

    d.box(11, 11.5, 18, 5, P["chip"])
    d.text(20, 14, "메트릭 이상 발견", size=10)
    d.box(41, 11.5, 18, 5, P["chip"])
    d.text(50, 14, "트레이스", size=10)
    d.arrow(29, 14, 41, 14, color=P["accent"], lw=2.0)
    d.text(35, 15.6, "exemplar 클릭", size=8, color=P["accent"], weight="bold")

    d.box(72, 15.5, 20, 4.6, P["chip"])
    d.text(82, 17.8, "로그", size=10)
    d.box(72, 6.4, 20, 4.6, P["chip"])
    d.text(82, 8.7, "플레임그래프", size=10)
    d.arrow(59, 15, 72, 17.8, color=P["accent"], lw=2.0)
    d.text(65, 18.6, "trace→logs", size=8, color=P["accent"], weight="bold")
    d.arrow(59, 13, 72, 8.7, color=P["accent"], lw=2.0)
    d.text(65, 10.2, "trace→profiles", size=8, color=P["accent"], weight="bold")


diagram("32-isolated-vs-correlated", draw, w=13, h=6.2, ymax=44)

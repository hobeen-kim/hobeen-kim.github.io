"""CH1 학습 패러다임 3종 비교 — 지도/비지도/강화 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    cols = [
        ("지도 학습", P["blue"],
         "입력 X + 정답 y", "정답과의 오차 최소화",
         "회귀 · 분류\n이탈·수요 예측"),
        ("비지도 학습", P["green"],
         "입력 X (정답 없음)", "데이터 구조 발견",
         "군집화 · 차원 축소\n이상 탐지"),
        ("강화 학습", P["purple"],
         "상태 + 보상 신호", "누적 보상 최대화",
         "제어 · 게임\n추천 정책"),
    ]
    w, gap = 28, 4
    x0 = 3
    for i, (title, fc, feed, goal, ex) in enumerate(cols):
        x = x0 + i * (w + gap)
        d.box(x, 4, w, 38, fc)
        d.text(x + w / 2, 38, title, size=11.5, weight="bold")
        d.box(x + 3, 27, w - 6, 7, P["chip"])
        d.text(x + w / 2, 30.5, feed, size=9, color=P["dim"])
        d.box(x + 3, 17, w - 6, 7, P["chip"])
        d.text(x + w / 2, 20.5, goal, size=9, color=P["dim"])
        d.text(x + w / 2, 9.5, ex, size=8.8, color=P["dim"], style="italic")
        d.text(x + w / 2, 35, "무엇을 받나 / 목표 / 예", size=7.6, color=P["dim"])


diagram("01-learning-paradigms", draw, w=13, h=5.0, ymax=46)

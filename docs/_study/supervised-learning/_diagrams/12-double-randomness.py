"""CH12 랜덤 포레스트 이중 무작위화 — 부트스트랩(행) + max_features(열) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 원본 데이터
    d.box(3, 18, 16, 12, P["chip"])
    d.text(11, 27, "원본 데이터", size=9.5)
    d.text(11, 22.5, "행=샘플\n열=피처", size=8, color=P["dim"])

    # 트리 3개: 각자 다른 행 표본 + 다른 열 부분집합
    picks = [
        ("행 표본 A\n피처 {1,3,4}", 32),
        ("행 표본 B\n피처 {2,3,5}", 21),
        ("행 표본 C\n피처 {1,2,4}", 10),
    ]
    for i, (lab, y) in enumerate(picks):
        d.box(26, y, 16, 8, P["gray"])
        d.text(34, y + 4, lab, size=8, color=P["dim"])
        d.box(48, y, 12, 8, P["green"])
        d.text(54, y + 4, f"트리 {i+1}", size=9)
        d.arrow(19, 24, 26, y + 4, color=P["edge"], lw=1.2, rad=0.04)
        d.arrow(42, y + 4, 48, y + 4, color=P["edge"], lw=1.4)

    d.text(34, 6, "부트스트랩(행) + 노드마다 max_features(열)",
           size=8.4, color=P["dim"], style="italic")

    # 집계
    d.box(66, 17, 12, 10, P["blue"])
    d.text(72, 22, "다수결/\n평균", size=9)
    for _, y in picks:
        d.arrow(60, y + 4, 66, 22, color=P["edge"], lw=1.2, rad=0.05)
    d.box(84, 18, 12, 8, P["purple"])
    d.text(90, 22, "예측", size=9.5)
    d.arrow(78, 22, 84, 22, color=P["accent"], lw=1.8)


diagram("12-double-randomness", draw, w=13, h=4.6, ymax=40)

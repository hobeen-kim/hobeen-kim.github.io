"""CH11 편향-분산 관점 재방문 — 배깅=분산↓, 부스팅=편향↓ (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 축: 가로=편향, 세로=분산 (개념도)
    d.arrow(12, 8, 12, 42, color=P["edge"], lw=1.5)
    d.text(9.5, 40, "분산", size=9.5, color=P["dim"], ha="right")
    d.arrow(12, 8, 94, 8, color=P["edge"], lw=1.5)
    d.text(92, 5, "편향", size=9.5, color=P["dim"])

    # 단일 깊은 트리 = 저편향·고분산 (왼쪽 위)
    d.box(18, 31, 22, 9, P["green"])
    d.text(29, 35.5, "단일 깊은 트리\n저편향·고분산", size=8.8)
    # 배깅: 분산을 내린다 (아래로 화살표)
    d.arrow(29, 31, 29, 18, color=P["green"], lw=2.2)
    d.text(31, 24, "배깅\n분산↓", size=8.8, color=P["green"], ha="left")
    d.box(18, 10, 22, 7, P["chip"])
    d.text(29, 13.5, "랜덤 포레스트", size=8.8, color=P["dim"])

    # 단일 얕은 트리 = 고편향·저분산 (오른쪽 아래)
    d.box(66, 11, 22, 9, P["brown"])
    d.text(77, 15.5, "얕은 그루터기\n고편향·저분산", size=8.8)
    # 부스팅: 편향을 내린다 (왼쪽으로 화살표)
    d.arrow(66, 15.5, 48, 15.5, color=P["brown"], lw=2.2)
    d.text(57, 18, "부스팅 · 편향↓", size=8.8, color=P["brown"])
    d.box(44, 11.5, 12, 7, P["chip"])
    d.text(50, 15, "GBDT", size=8.8, color=P["dim"])

    d.text(53, 44, "같은 트리, 반대 방향으로 튜닝한다", size=9.5,
           color=P["dim"], style="italic")


diagram("11-bias-variance-view", draw, w=12, h=5.2, ymax=48)

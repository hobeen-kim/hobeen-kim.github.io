"""CH12 OOB 평가 — 부트스트랩에서 빠진 샘플이 공짜 검증셋 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 상단: 한 트리의 부트스트랩 표본 — 뽑힌 샘플(in-bag) / 빠진 샘플(OOB)
    d.text(50, 43, "한 그루의 부트스트랩 (복원 추출)", size=10,
           weight="bold")
    n = 10
    x0, w = 8, 8
    picked = {0, 1, 2, 4, 5, 7, 9}  # in-bag(중복 포함), 나머지는 OOB
    for i in range(n):
        x = x0 + i * (w + 0.6)
        if i in picked:
            d.box(x, 30, w, 7, P["green"])
            d.text(x + w / 2, 33.5, f"#{i}", size=8.5)
        else:
            d.box(x, 30, w, 7, P["chip"], ec=P["orange"], lw=1.6)
            d.text(x + w / 2, 33.5, f"#{i}", size=8.5, color=P["orange"])

    d.text(50, 25.5, "약 37%는 한 번도 안 뽑힌다  →  이 트리의 OOB 샘플",
           size=8.6, color=P["dim"], style="italic")

    # 하단: OOB 샘플 → 그 샘플을 안 본 트리들만 모아 예측 → OOB 점수
    d.box(6, 8, 24, 10, P["chip"], ec=P["orange"], lw=1.6)
    d.text(18, 13, "OOB 샘플\n(#3, #6, #8 …)", size=8.6, color=P["orange"])
    d.box(40, 8, 24, 10, P["green"])
    d.text(52, 13, "그 샘플을 학습에\n안 쓴 트리들만", size=8.6)
    d.box(74, 8, 20, 10, P["blue"])
    d.text(84, 13, "OOB 점수\n= 공짜 검증", size=8.6)
    d.arrow(30, 13, 40, 13, color=P["edge"], lw=1.6)
    d.arrow(64, 13, 74, 13, color=P["accent"], lw=1.8)


diagram("12-oob-evaluation", draw, w=13, h=5.0, ymax=46)

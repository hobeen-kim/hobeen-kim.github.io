"""다중 클래스 전략 — 소프트맥스(단일 다항) · OvR · OvO (3클래스 A/B/C 예시) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    colw = 30
    xs = [2, 35, 68]

    # --- 소프트맥스 (다항 로지스틱): 모델 1개, 출력 K개 ---
    x = xs[0]
    d.text(x + colw / 2, 30, "소프트맥스 (다항)", size=11, weight="bold")
    d.box(x + 6, 20, colw - 12, 6, P["purple"])
    d.text(x + colw / 2, 23, "단일 모델", size=9.5)
    for i, (c, lab) in enumerate([("A", "P(A)"), ("B", "P(B)"), ("C", "P(C)")]):
        bx = x + i * (colw / 3) + 1
        d.box(bx, 9, colw / 3 - 2, 5, P["green"])
        d.text(bx + colw / 6 - 1, 11.5, lab, size=9, color=P["dim"])
        d.arrow(x + colw / 2, 20, bx + colw / 6 - 1, 14.3, color=P["accent"], lw=1.3)
    d.text(x + colw / 2, 5.5, "합이 1인 확률 분포", size=8.8, color=P["dim"])

    # --- OvR: 클래스마다 이진 분류기 K개 ---
    x = xs[1]
    d.text(x + colw / 2, 30, "OvR (일대다)", size=11, weight="bold")
    for i, lab in enumerate(["A vs 나머지", "B vs 나머지", "C vs 나머지"]):
        by = 22 - i * 6
        d.box(x + 3, by, colw - 6, 4.6, P["blue"])
        d.text(x + colw / 2, by + 2.3, lab, size=9, color=P["dim"])
    d.text(x + colw / 2, 3.5, "분류기 K개 → 최고 점수 선택", size=8.8, color=P["dim"])

    # --- OvO: 쌍마다 이진 분류기 K(K-1)/2개 ---
    x = xs[2]
    d.text(x + colw / 2, 30, "OvO (일대일)", size=11, weight="bold")
    for i, lab in enumerate(["A vs B", "A vs C", "B vs C"]):
        by = 22 - i * 6
        d.box(x + 3, by, colw - 6, 4.6, P["brown"])
        d.text(x + colw / 2, by + 2.3, lab, size=9, color=P["dim"])
    d.text(x + colw / 2, 3.5, "쌍마다 분류기 → 다수결 투표", size=8.8, color=P["dim"])


diagram("07-multiclass", draw, w=13, h=4.8, xmax=100, ymax=33)

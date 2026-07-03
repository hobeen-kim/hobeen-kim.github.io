"""CH3 혼동 행렬 → 정밀도/재현율 — 2x2 셀과 두 지표의 계산 방향 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 2x2 셀 좌표
    cw, ch = 20, 13
    x0, y0 = 30, 12  # 좌하단 기준
    cells = {
        (0, 1): ("TP", P["green"], "실제 P · 예측 P"),   # 좌상
        (1, 1): ("FN", P["brown"], "실제 P · 예측 N"),   # 우상
        (0, 0): ("FP", P["brown"], "실제 N · 예측 P"),   # 좌하
        (1, 0): ("TN", P["green"], "실제 N · 예측 N"),   # 우하
    }
    for (cx, cy), (label, fc, sub) in cells.items():
        x = x0 + cx * cw
        y = y0 + cy * ch
        d.box(x, y, cw, ch, fc)
        d.text(x + cw / 2, y + ch / 2 + 1.8, label, size=13, weight="bold")
        d.text(x + cw / 2, y + ch / 2 - 3, sub, size=7.6, color=P["dim"])

    # 축 라벨
    d.text(x0 + cw, y0 + 2 * ch + 3, "예측", size=10, weight="bold", color=P["accent"])
    d.text(x0 + cw / 2, y0 + 2 * ch + 0.5, "Positive", size=8.6, color=P["dim"])
    d.text(x0 + cw + cw / 2, y0 + 2 * ch + 0.5, "Negative", size=8.6, color=P["dim"])
    d.text(x0 - 6, y0 + ch + ch / 2, "실제 P", size=8.6, color=P["dim"], ha="right")
    d.text(x0 - 6, y0 + ch / 2, "실제 N", size=8.6, color=P["dim"], ha="right")

    # 정밀도: 예측 P 열(왼쪽 열) 방향
    d.box(x0 - 1, y0 - 1, cw + 2, 2 * ch + 2, P["chip"], ec=P["orange"], lw=1.8, alpha=0.0)
    d.arrow(x0 + cw / 2, y0 - 1.5, x0 + cw / 2, y0 - 6, color=P["orange"], lw=1.6)
    d.text(x0 + cw / 2, y0 - 8.5, "정밀도 = TP / (TP+FP)\n예측 P 중 진짜 P 비율",
           size=8.4, color=P["orange"])

    # 재현율: 실제 P 행(위쪽 행) 방향
    d.arrow(x0 + 2 * cw + 1.5, y0 + ch + ch / 2, x0 + 2 * cw + 7, y0 + ch + ch / 2,
            color=P["violet"], lw=1.6)
    d.text(x0 + 2 * cw + 9, y0 + ch + ch / 2, "재현율\n= TP / (TP+FN)\n실제 P 중\n잡아낸 비율",
           size=8.4, color=P["violet"], ha="left")


diagram("03-confusion-matrix", draw, w=12, h=6, ymax=52)

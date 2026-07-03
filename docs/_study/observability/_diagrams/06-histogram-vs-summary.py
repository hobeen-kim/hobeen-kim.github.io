"""CH06 §3 Histogram vs Summary — 분위수 계산 위치와 집계 가능성 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽: Histogram
    d.box(3, 6, 44, 38, P["green"], ec=P["accent"], lw=1.8)
    d.text(25, 40.5, "Histogram — 서버 계산 · 집계 가능", size=11, weight="bold",
           color=P["accent"])
    hsteps = [
        "클라이언트: 버킷 카운트만 누적\n(le = 0.1 · 0.5 · 1 · +Inf)",
        "여러 인스턴스 버킷 합산\nsum by (le)",
        "histogram_quantile()\n쿼리 시점에 분위수 계산",
    ]
    for i, t in enumerate(hsteps):
        yy = 29 - i * 8.5
        d.box(6, yy, 38, 6.5, P["chip"])
        d.text(25, yy + 3.25, t, size=9)
        if i < 2:
            d.arrow(25, yy, 25, yy - 2, color=P["accent"])

    # 오른쪽: Summary
    d.box(53, 6, 44, 38, P["brown"], ec=P["orange"], lw=1.6)
    d.text(75, 40.5, "Summary — 클라이언트 계산 · 집계 불가", size=11,
           weight="bold", color=P["orange"])
    ssteps = [
        "클라이언트: 분위수 직접 계산해 노출\n{quantile=\"0.5\"} …",
        "인스턴스별 값이 이미 확정\n재계산 불가",
        "여러 인스턴스 quantile 평균/합산\n수학적으로 의미 없음",
    ]
    for i, t in enumerate(ssteps):
        yy = 29 - i * 8.5
        d.box(56, yy, 38, 6.5, P["chip"])
        d.text(75, yy + 3.25, t, size=9)
        if i < 2:
            d.arrow(75, yy, 75, yy - 2, color=P["orange"])


diagram("06-histogram-vs-summary", draw, w=13, h=6.2, ymax=46)

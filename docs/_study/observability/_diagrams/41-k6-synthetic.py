"""CH41 k6 · Synthetic Monitoring — 능동적 관측 구조 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 왼쪽 위: k6 부하 테스트
    d.box(2, 26, 24, 18, P["green"])
    d.text(14, 41.5, "k6 — 부하 테스트", size=11, weight="bold")
    d.text(14, 39, "(JS 시나리오)", size=8.5, color=P["dim"])
    for i, t in enumerate([
        "VU · executor",
        "checks · thresholds",
        "k6 browser",
    ]):
        yy = 35.7 - i * 4.1
        d.box(4, yy - 1.7, 20, 3.4, P["chip"])
        d.text(14, yy, t, size=9)

    # 왼쪽 아래: Synthetic Monitoring 상시 프로브
    d.box(2, 3, 24, 19, P["blue"])
    d.text(14, 19, "Synthetic Monitoring", size=11, weight="bold")
    d.text(14, 16.7, "(상시 글로벌 프로브)", size=8.5, color=P["dim"])
    for i, t in enumerate([
        "HTTP · ping · DNS · TCP",
        "browser · scripted check",
        "traceroute",
    ]):
        yy = 13.5 - i * 4.0
        d.box(4, yy - 1.7, 20, 3.4, P["chip"])
        d.text(14, yy, t, size=9)

    # 중앙: 대상 시스템 (블랙박스)
    d.box(34, 17, 20, 17, P["brown"])
    d.text(44, 30, "대상 시스템", size=11.5, weight="bold")
    d.text(44, 27, "(API·웹·DNS·인증서)", size=9, color=P["dim"])
    d.text(44, 22.5, "내부 계측 없이\n외부 관점에서 측정", size=9, color=P["accent"], style="italic")

    # 오른쪽: 결과 → LGTM
    d.box(62, 10, 26, 30, P["gray"])
    d.text(75, 37, "결과 → LGTM 스택", size=11, weight="bold")
    for i, t in enumerate([
        "Mimir / Prometheus",
        "Loki",
        "Grafana 대시보드",
        "Alerting · SLO",
    ]):
        yy = 30 - i * 5.5
        d.box(64, yy - 2.2, 22, 4.4, P["chip"])
        d.text(75, yy, t, size=9.5)

    # 흐름 화살표
    d.arrow(26, 36, 34, 29, color=P["orange"])
    d.text(30, 34.5, "부하 주입", size=8, color=P["orange"])
    d.arrow(26, 12, 34, 21, color=P["accent"])
    d.text(29.5, 14.8, "정기 프로브", size=8, color=P["accent"])
    d.arrow(54, 25, 62, 24, color=P["violet"])
    d.text(58, 27, "메트릭·로그", size=8, color=P["violet"])

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="k6 부하 주입"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="Synthetic 프로브"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="결과 메트릭·로그 적재"),
    ])


diagram("41-k6-synthetic", draw, w=13, h=6.4, ymax=48)

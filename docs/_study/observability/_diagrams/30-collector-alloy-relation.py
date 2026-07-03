"""CH30 Collector와 Alloy — 포함 관계 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # OTel Collector (상단)
    d.box(30, 33, 40, 8, P["blue"], ec=P["accent"], lw=1.8)
    d.text(50, 38.2, "OpenTelemetry Collector", size=12, weight="bold",
           color=P["accent"])
    d.text(50, 35.0, "CNCF · 벤더 중립 코드베이스", size=9, color=P["dim"])

    # contrib (좌하)
    d.box(5, 17, 33, 9, P["gray"])
    d.text(21.5, 22.6, "otel-collector-contrib", size=10, weight="bold")
    d.text(21.5, 19.4, "커뮤니티 리시버/프로세서/익스포터", size=8, color=P["dim"])

    # Alloy (우하)
    d.box(54, 13, 41, 14, P["green"], ec=P["accent"], lw=1.8)
    d.text(74.5, 24.0, "Grafana Alloy", size=12, weight="bold", color=P["accent"])
    d.text(74.5, 20.6, "Collector 임베드 + Alloy 구문", size=9, color=P["dim"])
    d.text(74.5, 17.0, "+ prometheus.* / loki.* / pyroscope.*\n네이티브 컴포넌트",
           size=8.4)

    # Agent (최하)
    d.box(54, 3, 41, 6.5, P["brown"])
    d.text(74.5, 7.6, "Grafana Agent", size=10.5, weight="bold")
    d.text(74.5, 4.8, "EOL · Alloy로 이관 완료", size=8.3, color=P["dim"])

    # edges
    d.arrow(38, 34, 24, 26, color=P["accent"], lw=1.9)
    d.arrow(64, 34, 72, 27, color=P["accent"], lw=2.1)
    d.text(71, 31, "코드베이스 임베드", size=8.3, color=P["orange"], weight="bold")
    d.arrow(74.5, 9.5, 74.5, 13, color=P["violet"], lw=1.9, ls=(0, (4, 3)))
    d.text(82, 11.3, "후속", size=8.3, color=P["violet"], weight="bold")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.4, label="파생 · 임베드"),
        Line2D([0], [0], color=P["violet"], lw=2.4, ls="--", label="후속 이관"),
    ], loc="upper left", anchor=(0.02, 0.42))


diagram("30-collector-alloy-relation", draw, w=13, h=6.0, ymax=42)

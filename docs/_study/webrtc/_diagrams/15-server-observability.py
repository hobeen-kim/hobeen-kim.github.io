"""CH15 §6 서버 측 관측 — 클라이언트 요약·TURN·SFU 신호를 Prometheus/Loki/Grafana로 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def label(x, y, s, color, size=8.5):
        d.ax.text(x, y, s, fontsize=size, color=color, ha="center",
                  va="center", zorder=6,
                  bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.2))

    # 신호 소스
    d.text(13, 51.5, "신호 소스", size=10, weight="bold", color=P["dim"])
    d.box(2, 40, 22, 8.5, P["green"])
    d.text(13, 44.25, "운영자 브라우저\n(getStats 요약)", size=9.5)
    d.box(2, 28, 22, 8.5, P["green"])
    d.text(13, 32.25, "디바이스\n(Pion·GStreamer 통계)", size=9.5)
    d.box(2, 16, 22, 8.5, P["brown"])
    d.text(13, 20.25, "TURN 서버\n(coturn)", size=9.5)
    d.box(2, 4, 22, 8.5, P["brown"])
    d.text(13, 8.25, "SFU · 시그널링 서버", size=9.5)

    # 수집
    d.box(36, 36, 20, 10, P["gray"])
    d.text(46, 41, "수집 API\n(세션 요약 수신)", size=9.5)
    d.box(64, 33, 16, 9, P["blue"])
    d.text(72, 37.5, "Loki\n(로그)", size=9.5)
    d.box(64, 12, 16, 9, P["blue"])
    d.text(72, 16.5, "Prometheus\n(메트릭)", size=9.5)
    d.box(86, 21, 13, 12, P["purple"], ec=P["accent"], lw=1.8)
    d.text(92.5, 27, "Grafana\n(대시보드\n· 알림)", size=9.5)

    # 소스 → 수집 API
    d.arrow(24, 44.25, 36, 42.5)
    label(30, 45.6, "10초 요약", P["dim"])
    d.arrow(24, 32.25, 36, 38.5)
    label(28.3, 37.6, "MQTT·HTTPS", P["dim"])

    # 수집 API → Loki / Prometheus
    d.arrow(56, 41, 64, 38.5, color=P["violet"])
    d.arrow(50, 36, 66, 21, color=P["orange"])
    label(52.6, 33.6, "지표 노출", P["orange"])

    # TURN·SFU → Prometheus (pull)
    d.arrow(24, 19, 64, 16.5, color=P["orange"])
    label(43, 19.4, "scrape :9641 (--prometheus)", P["orange"])
    d.arrow(24, 8.25, 64, 14, color=P["orange"])
    label(43, 9.4, "scrape /metrics", P["orange"])

    # TURN·SFU 로그 → Loki
    d.arrow(24, 22, 64, 34.5, color=P["violet"], ls="--", rad=0.15)
    label(36, 25.0, "세션 로그 (수집 에이전트)", P["violet"])

    # → Grafana
    d.arrow(80, 37.5, 86, 30, color=P["accent"])
    d.arrow(80, 16.5, 86, 24, color=P["accent"])


diagram("15-server-observability", draw, w=13, h=6.8, ymax=54)

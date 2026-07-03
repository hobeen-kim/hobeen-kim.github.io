"""README 학습 로드맵 — S1~S10 단계 체인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("S1", "관측성 기초 (01~04)",
         ["모니터링 vs 관측성", "4대 신호", "Grafana 스택", "Pull/Push·카디널리티"], P["gray"]),
        ("S2", "메트릭 — Prometheus (05~12)",
         ["아키텍처", "데이터 모델", "스크레이핑·SD", "Exporter", "PromQL", "TSDB·remote_write"], P["green"]),
        ("S3", "알림 — Alertmanager (13~15)",
         ["아키텍처·라우팅", "SLO/SLI 알림 설계"], P["brown"]),
        ("S4", "로그 — Loki (16~19)",
         ["아키텍처·라벨 철학", "읽기/쓰기 경로", "LogQL·파이프라인"], P["blue"]),
        ("S5", "트레이스 — Tempo & OTel (20~23)",
         ["분산 트레이싱 기초", "OpenTelemetry", "Tempo·TraceQL"], P["green"]),
        ("S6", "프로파일 — Pyroscope (24~27)",
         ["연속 프로파일링", "Pyroscope·eBPF", "플레임그래프"], P["brown"]),
        ("S7", "수집 파이프라인 — Alloy (28~30)",
         ["컴포넌트 모델·파이프라인", "Collector vs Alloy"], P["blue"]),
        ("S8", "통합 — Grafana (31~33)",
         ["데이터소스·대시보드", "상관관계·as-code"], P["gray"]),
        ("S9", "운영 심화 — SRE (34~38)",
         ["카디널리티·비용", "Mimir 장기저장", "HA·멀티테넌시", "K8s 배포·트러블슈팅"], P["purple"]),
        ("S10", "생태계 확장 (39~42)",
         ["Beyla eBPF 자동계측", "Faro 프런트엔드 RUM", "k6·Synthetic", "Grafana Alerting·IRM"], P["green"]),
    ]

    col_x = [27, 73]
    row_cy = [55, 43.5, 32, 20.5, 9]
    BW, BH = 42, 9.2

    def wrap_chain(steps):
        if len(steps) <= 3:
            return "  →  ".join(steps)
        mid = (len(steps) + 1) // 2
        return "  →  ".join(steps[:mid]) + "  →\n" + "  →  ".join(steps[mid:])

    positions = []
    for i, (tag, title, steps, fc) in enumerate(stages):
        row, col = i // 2, i % 2
        cx, cy = col_x[col], row_cy[row]
        positions.append((cx, cy))
        ec = P["accent"] if tag == "S10" else P["edge"]
        lw = 2.2 if tag == "S10" else 1.5
        d.box(cx - BW / 2, cy - BH / 2, BW, BH, fc, ec=ec, lw=lw)
        d.box(cx - BW / 2 + 1.2, cy + BH / 2 - 3.4, 6.5, 2.6, P["bg"], ec=ec, lw=1.2, r=0.02)
        d.text(cx - BW / 2 + 4.45, cy + BH / 2 - 2.1, tag, size=9.5, weight="bold",
               color=P["accent"] if tag == "S10" else P["text"])
        d.text(cx + 3, cy + BH / 2 - 2.1, title, size=10.5, weight="bold")
        d.text(cx, cy - 1.3, wrap_chain(steps), size=8.2, color=P["dim"])

    for i in range(len(stages) - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i + 1]
        if i % 2 == 0:
            d.arrow(x1 + BW / 2, y1, x2 - BW / 2, y2, color=P["accent"], lw=2.0)
        else:
            d.arrow(x1, y1 - BH / 2, x2, y2 + BH / 2, color=P["accent"], lw=2.0)


diagram("readme-roadmap", draw, w=15, h=9, ymax=62)

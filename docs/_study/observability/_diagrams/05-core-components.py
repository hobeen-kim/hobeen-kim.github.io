"""CH5 §2 핵심 컴포넌트 — Prometheus 단일 프로세스 내부 구조 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # Prometheus 서버 (단일 프로세스) 그룹
    d.box(30, 4, 44, 40, P["gray"], ec=P["accent"], lw=1.8)
    d.text(52, 41.2, "Prometheus 서버 (단일 프로세스)", size=11,
           weight="bold", color=P["accent"])

    # 내부 4 컴포넌트
    d.box(33, 28, 18, 9, P["blue"])
    d.text(42, 32.5, "Retrieval\n(scrape manager)", size=10)
    d.box(53, 28, 18, 9, P["brown"])
    d.text(62, 32.5, "TSDB\n(WAL + 블록 스토리지)", size=10)
    d.box(33, 8, 18, 9, P["green"])
    d.text(42, 12.5, "HTTP Server /\nPromQL 엔진", size=10)
    d.box(53, 8, 18, 9, P["purple"])
    d.text(62, 12.5, "Rule Manager\n(recording / alerting)", size=10)

    # 외부 요소
    d.box(2, 34, 20, 8, P["chip"])
    d.text(12, 38, "Service Discovery", size=10)
    d.box(2, 22, 20, 8, P["chip"])
    d.text(12, 26, "스크레이프 타깃\n(/metrics)", size=10)
    d.box(2, 8, 20, 8, P["chip"])
    d.text(12, 12, "사용자 / Grafana", size=10)
    d.box(78, 8, 20, 9, P["chip"])
    d.text(88, 12.5, "Alertmanager", size=10)

    # 화살표
    d.arrow(22, 38, 33, 34.5)
    d.text(27, 38.3, "타깃 목록", size=8, color=P["dim"])
    d.arrow(22, 26, 33, 30.5)
    d.text(27, 26.3, "pull", size=8, color=P["dim"])
    d.arrow(51, 32.5, 53, 32.5)
    d.text(52, 34.3, "append", size=8, color=P["dim"])
    d.arrow(44, 17, 58, 28, color=P["orange"])
    d.text(48, 22.5, "질의", size=8, color=P["orange"])
    d.arrow(63.5, 17, 63.5, 28, color=P["violet"])
    d.text(67.8, 22.5, "PromQL 평가", size=8, color=P["violet"])
    d.arrow(22, 12, 33, 12)
    d.text(27, 13.8, "PromQL", size=8, color=P["dim"])
    d.arrow(71, 12.5, 78, 12.5, color=P["orange"])
    d.text(74.5, 14.3, "알림 전송", size=8, color=P["orange"])


diagram("05-core-components", draw, w=12, h=6.2, ymax=48)

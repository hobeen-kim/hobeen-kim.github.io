"""CH35 Mimir 마이크로서비스 아키텍처 — 쓰기·저장·압축·읽기 경로 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # ---- group backgrounds ----
    d.box(3.5, 27.5, 23, 20.5, P["chip"], ec=P["edge"], lw=1.0)
    d.text(5, 46.3, "쓰기 경로", size=9.5, color=P["dim"], ha="left")
    d.box(73.5, 15.5, 23, 32.5, P["chip"], ec=P["edge"], lw=1.0)
    d.text(75, 46.3, "읽기 경로", size=9.5, color=P["dim"], ha="left")
    d.box(39.5, 22, 21, 10, P["chip"], ec=P["edge"], lw=1.0)
    d.text(41, 30.5, "압축", size=9.5, color=P["dim"], ha="left")
    d.box(39.5, 7.5, 21, 12, P["chip"], ec=P["edge"], lw=1.0)
    d.text(41, 18.0, "오브젝트 스토리지", size=9.5, color=P["dim"], ha="left")

    # ---- write column ----
    d.box(6, 50, 18, 5.6, P["gray"])
    d.text(15, 52.8, "Prometheus\n(remote_write)", size=9, weight="bold")
    d.box(6, 39.5, 18, 6.2, P["blue"])
    d.text(15, 42.6, "distributor\n검증·limit·라우팅", size=9)
    d.box(6, 29, 18, 6.2, P["blue"])
    d.text(15, 32.1, "ingester\n메모리 + WAL", size=9)

    # ---- center ----
    d.box(41, 23, 18, 6.2, P["brown"])
    d.text(50, 26.1, "compactor\n병합·dedup", size=9)
    d.box(41, 9, 18, 7.2, P["green"])
    d.text(50, 12.6, "S3 / GCS / Blob\n(TSDB 블록)", size=9)

    # ---- read column ----
    d.box(76, 50, 18, 5.6, P["gray"])
    d.text(85, 52.8, "Grafana", size=10, weight="bold")
    d.box(76, 39.5, 18, 6.2, P["purple"])
    d.text(85, 42.6, "query-frontend\n분할·캐시", size=9)
    d.box(76, 29, 18, 6.2, P["purple"])
    d.text(85, 32.1, "querier", size=10)
    d.box(76, 17, 18, 6.2, P["purple"])
    d.text(85, 20.1, "store-gateway\n블록 인덱스 캐시", size=9)

    # ---- write arrows ----
    d.arrow(15, 50, 15, 45.7, color=P["accent"], lw=2.0)
    d.text(28, 48, "remote_write", size=8, color=P["accent"])
    d.arrow(15, 39.5, 15, 35.2, color=P["accent"], lw=2.0)
    d.text(24, 37.5, "복제 (RF=3)", size=8, color=P["accent"])
    d.arrow(23, 30, 41, 14, color=P["orange"], lw=2.0)
    d.text(31, 24.5, "블록 flush", size=8, color=P["orange"])

    # ---- compact <-> storage ----
    d.arrow(47.5, 23, 47.5, 16.2, color=P["orange"], lw=1.8)
    d.text(40, 19.7, "병합·재작성", size=8, color=P["orange"], ha="right")
    d.arrow(52.5, 16.2, 52.5, 23, color=P["orange"], lw=1.8)

    # ---- read arrows ----
    d.arrow(85, 50, 85, 45.7, color=P["violet"], lw=2.0)
    d.text(85, 47.9, "PromQL", size=8, color=P["violet"])
    d.arrow(85, 39.5, 85, 35.2, color=P["violet"], lw=2.0)
    d.arrow(85, 29, 85, 23.2, color=P["violet"], lw=2.0)
    d.text(96, 26, "과거 데이터", size=8, color=P["violet"], ha="right")
    d.arrow(76, 32.1, 24, 32.1, color=P["violet"], lw=1.8)
    d.text(50, 33.6, "최근 데이터", size=8, color=P["violet"])
    d.arrow(76, 19, 59, 13.5, color=P["violet"], lw=1.8)
    d.text(69, 15.2, "블록 조회", size=8, color=P["violet"])

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.4, label="쓰기 경로 (수집)"),
        Line2D([0], [0], color=P["orange"], lw=2.4, label="블록 flush·압축"),
        Line2D([0], [0], color=P["violet"], lw=2.4, label="읽기 경로 (쿼리)"),
    ], loc="lower left", anchor=(0.005, 0.02))


diagram("35-mimir-architecture", draw, w=15, h=8.6, ymax=58)

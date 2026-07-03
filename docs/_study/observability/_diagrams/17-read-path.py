"""CH17 읽기 경로 — query-frontend → querier → ingester + storage 병합 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(36, 48, 28, 6, P["blue"])
    d.text(50, 51, "사용자 / Grafana", size=11, weight="bold")

    d.box(34, 38, 32, 6, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 42, "Query-Frontend", size=11, weight="bold", color=P["accent"])
    d.text(50, 39.4, "쿼리 분할 + 캐싱", size=8.5, color=P["dim"])

    d.box(38, 28, 24, 6, P["green"])
    d.text(50, 31, "Querier", size=11, weight="bold")

    # 세 소스
    d.box(4, 13, 26, 8, P["green"], ec=P["accent"], lw=1.4)
    d.text(17, 18, "Ingester", size=10.5, weight="bold")
    d.text(17, 15, "미flush 최신", size=8.5, color=P["dim"])

    d.box(37, 13, 26, 8, P["gray"])
    d.text(50, 18, "Index (TSDB)", size=10.5, weight="bold")
    d.text(50, 15, "청크 위치 조회", size=8.5, color=P["dim"])

    d.box(70, 13, 26, 8, P["brown"])
    d.text(83, 18, "오브젝트 스토리지", size=10.5, weight="bold")
    d.text(83, 15, "flush된 과거 청크", size=8.5, color=P["dim"])

    d.box(30, 3, 40, 6, P["blue"], ec=P["accent"], lw=1.4)
    d.text(50, 6, "시간순 병합 → 결과 반환", size=11, weight="bold")

    d.arrow(50, 48, 50, 44, color=P["accent"])
    d.arrow(50, 38, 50, 34, color=P["accent"])
    d.arrow(45, 28, 17, 21, color=P["orange"])
    d.text(28, 25.6, "최신", size=8, color=P["orange"])
    d.arrow(50, 28, 50, 21, color=P["orange"])
    d.text(58, 24.5, "청크 위치", size=8, color=P["orange"])
    d.arrow(55, 28, 83, 21, color=P["orange"])
    d.text(72, 25.6, "과거 청크", size=8, color=P["orange"])
    d.arrow(17, 13, 34, 9, color=P["accent"])
    d.arrow(83, 13, 66, 9, color=P["accent"])
    d.arrow(63, 16.5, 70, 16.5, color=P["dim"], ls="--", lw=1.3)


diagram("17-read-path", draw, w=12, h=6.4, ymax=56)

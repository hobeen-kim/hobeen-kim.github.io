"""CH12 PromQL 쿼리 — index 역인덱스 조회 경로 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    yc = 16
    # 1. PromQL 쿼리
    d.box(3, 8, 22, 16, P["blue"])
    d.text(14, 20, "PromQL 쿼리", size=11, weight="bold")
    d.text(14, 15, '{job="api",\nstatus_code="500"}', size=9.5, color=P["dim"])

    # 2. Index
    d.box(28, 8, 22, 16, P["gray"], ec=P["accent"], lw=1.8)
    d.text(39, 20, "Index", size=11, weight="bold", color=P["accent"])
    d.text(39, 15, "역인덱스\n(라벨 → 시계열 ID)", size=9.5)

    # 3. 매칭 ID
    d.box(54, 8, 20, 16, P["green"])
    d.text(64, 20, "매칭 시계열 ID", size=11, weight="bold")
    d.text(64, 15, "job=api 집합\n∩ status=500 집합", size=9, color=P["dim"])

    # 4. Chunk 읽기
    d.box(78, 8, 20, 16, P["brown"])
    d.text(88, 20, "Chunk 읽기", size=11, weight="bold")
    d.text(88, 15, "매칭 ID의\nchunk만 스캔", size=9, color=P["dim"])

    d.arrow(25, yc, 28, yc, color=P["accent"])
    d.arrow(50, yc, 54, yc, color=P["accent"])
    d.text(52, 18.5, "교집합", size=8, color=P["accent"])
    d.arrow(74, yc, 78, yc, color=P["accent"])


diagram("12-query-index", draw, w=13, h=5, ymax=30)

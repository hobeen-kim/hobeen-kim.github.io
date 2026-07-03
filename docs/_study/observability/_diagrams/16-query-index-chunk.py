"""CH16 쿼리 흐름 — 인덱스로 좁히고 청크만 로드 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 세로 흐름 (좌측)
    d.box(24, 40, 40, 7, P["blue"])
    d.text(44, 45, "LogQL 쿼리", size=11, weight="bold")
    d.text(44, 42.2, '{app="checkout"} |= "timeout"', size=9, color=P["accent"])

    d.box(24, 28, 40, 7, P["gray"], ec=P["accent"], lw=1.8)
    d.text(44, 33, "인덱스 (TSDB)", size=11, weight="bold", color=P["accent"])
    d.text(44, 30.2, "라벨 → 청크 참조 (작은 테이블)", size=9, color=P["dim"])

    d.box(24, 16, 40, 7, P["green"])
    d.text(44, 21, "대상 청크만 로드", size=11, weight="bold")
    d.text(44, 18.2, "좁혀진 청크 목록만", size=9, color=P["dim"])

    d.box(24, 4, 40, 7, P["blue"])
    d.text(44, 7.5, "라인 필터 / 파서 → 결과", size=10.5, weight="bold")

    # 오브젝트 스토리지 (우측)
    d.box(72, 15, 24, 20, P["brown"])
    d.text(84, 29, "오브젝트\n스토리지", size=11, weight="bold")
    d.text(84, 21, "압축 로그 청크\n(S3/GCS)", size=9, color=P["dim"])

    d.arrow(44, 40, 44, 35, color=P["orange"])
    d.text(58, 37.6, "1. 라벨 매처 조회", size=8, color=P["orange"])
    d.arrow(44, 28, 44, 23, color=P["orange"])
    d.text(58, 25.6, "2. 청크 참조", size=8, color=P["orange"])
    d.arrow(64, 19.5, 72, 22, color=P["orange"])
    d.text(68, 16.8, "3. fetch", size=8, color=P["orange"])
    d.arrow(44, 16, 44, 11, color=P["accent"])


diagram("16-query-index-chunk", draw, w=12, h=6.4, ymax=50)

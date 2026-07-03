"""CH22 Tempo 설계 — 전통적 인덱스 백엔드 vs 오브젝트 스토리지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def cbox(cx, cy, w, h, fc, **kw):
        d.box(cx - w / 2, cy - h / 2, w, h, fc, **kw)

    # 왼쪽: 전통적 백엔드
    d.box(4, 6, 40, 38, P["gray"])
    d.text(24, 41, "전통적 트레이싱 백엔드", size=12, weight="bold", color=P["orange"])
    cbox(24, 35, 26, 6, P["blue"])
    d.text(24, 35, "Trace 데이터", size=10.5, weight="bold")
    cbox(24, 25, 30, 7, P["brown"])
    d.text(24, 26.3, "전용 검색 인덱스", size=10.5, weight="bold")
    d.text(24, 23.6, "Elasticsearch 등", size=8, color=P["dim"])
    cbox(24, 14, 22, 6, P["green"])
    d.text(24, 14, "쿼리", size=10.5, weight="bold")
    d.arrow(24, 32, 24, 28.5, color=P["orange"])
    d.arrow(24, 21.5, 24, 17, color=P["orange"])

    # 오른쪽: Tempo
    d.box(56, 6, 40, 38, P["gray"], ec=P["accent"], lw=1.8)
    d.text(76, 41, "Tempo", size=12, weight="bold", color=P["accent"])
    cbox(76, 35, 26, 6, P["blue"])
    d.text(76, 35, "Trace 데이터", size=10.5, weight="bold")
    cbox(76, 26, 30, 6.5, P["brown"])
    d.text(76, 26, "블록 (오브젝트 스토리지)", size=10, weight="bold")
    cbox(66, 16, 18, 7, P["green"])
    d.text(66, 17.3, "Bloom filter", size=9, weight="bold")
    d.text(66, 14.7, "trace ID 존재 여부", size=7.6, color=P["dim"])
    cbox(87, 16, 16, 7, P["purple"])
    d.text(87, 17.3, "TraceQL", size=9, weight="bold")
    d.text(87, 14.7, "블록 스캔", size=7.6, color=P["dim"])
    d.arrow(76, 32, 76, 29.5, color=P["accent"])
    d.arrow(72, 22.5, 68, 19.7, color=P["accent"])
    d.arrow(80, 22.5, 85, 19.7, color=P["accent"])
    d.text(66, 10.4, "trace ID 조회 (빠름·주경로)", size=8, color=P["accent"])
    d.text(87, 10.4, "속성 검색 (드묾·스캔)", size=8, color=P["violet"])


diagram("22-tempo-design", draw, w=13, h=6, ymax=46)

"""CH25 Pyroscope 저장 구조 — 오브젝트 스토리지 · 심볼 DB (light/dark PNG)."""
from _common import diagram
from _common import Line2D


def draw(d):
    P = d.P

    def node(x, y, w, h, t, sub, c, ec=None, lw=1.4):
        d.box(x, y, w, h, c, ec=ec, lw=lw)
        d.text(x + w / 2, y + h * 0.62, t, size=10.5, weight="bold")
        if sub:
            d.text(x + w / 2, y + h * 0.26, sub, size=8, color=P["dim"])

    node(6, 43, 20, 8, "distributor", "수집 경로에서 유입", P["gray"],
         ec=P["accent"], lw=1.8)
    node(40, 43, 22, 8, "ingester", "메모리 버퍼", P["blue"])
    node(72, 41, 24, 10, "오브젝트 스토리지", "S3 / GCS / Blob\n블록 저장", P["brown"],
         ec=P["orange"], lw=1.6)
    node(40, 27, 22, 8, "심볼 DB", "주소 → 함수명 캐시", P["purple"])
    node(72, 27, 24, 8, "compactor", "블록 병합 · 보존", P["green"])
    node(40, 12, 22, 8, "store-gateway", "블록 조회 게이트웨이", P["gray"])
    node(72, 12, 24, 8, "querier", "프로파일 병합 질의", P["gray"],
         ec=P["accent"], lw=1.8)

    # 화살표
    d.arrow(26, 47, 40, 47, color=P["accent"], lw=2.0)
    d.arrow(62, 46, 72, 46, color=P["orange"], lw=2.0)
    d.text(67, 48, "블록 플러시", size=8, color=P["orange"])
    d.arrow(51, 43, 51, 35, color=P["violet"], lw=1.8, ls=(0, (5, 3)))
    d.text(55.5, 39, "심볼 정보", size=8, color=P["violet"], ha="left")
    d.arrow(84, 41, 84, 35, color=P["green"], lw=2.0)
    d.arrow(72, 44, 62, 18, color=P["edge"], lw=1.8)
    d.text(69.5, 31.5, "블록 로드", size=8, color=P["dim"], ha="left")
    d.arrow(62, 16, 72, 16, color=P["accent"], lw=2.0)
    d.arrow(51, 27, 78, 20, color=P["violet"], lw=1.8, ls=(0, (5, 3)))
    d.text(66, 24, "심볼 주입", size=8, color=P["violet"])

    leg = [
        Line2D([0], [0], color=P["orange"], lw=2.2, label="블록 플러시·저장"),
        Line2D([0], [0], color=P["accent"], lw=2.2, label="질의 경로"),
        Line2D([0], [0], color=P["violet"], lw=2.2, ls="--",
               label="심볼 정보 (주소→함수명)"),
    ]
    d.legend(leg, anchor=(0.005, 0.02))


diagram("25-storage-architecture", draw, w=13, h=7, ymax=54)

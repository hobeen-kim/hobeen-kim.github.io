"""CH17 §5 Kinesis Video Streams의 두 기능 — WebRTC(실시간)와 Video Streams(저장·재생), 그리고 연결 고리 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ── 위: WebRTC ──
    d.box(2, 30, 96, 18, P["gray"])
    d.text(4, 45.8, "KVS WebRTC — 실시간 (P2P)", size=9.5, weight="bold",
           ha="left")
    d.box(5, 33, 15, 9, P["green"])
    d.text(12.5, 37.5, "디바이스\n(C SDK, Master)", size=8.5)
    d.box(40, 37, 20, 7, P["chip"], ec=P["violet"], lw=1.4)
    d.text(50, 40.5, "시그널링 채널\nSTUN / TURN", size=8.5)
    d.box(80, 33, 15, 9, P["blue"])
    d.text(87.5, 37.5, "브라우저\n(Viewer)", size=8.5)
    d.arrow(20, 40.5, 40, 40.5, color=P["violet"], ls="--", lw=1.3,
            style="<|-|>")
    d.arrow(60, 40.5, 80, 40.5, color=P["violet"], ls="--", lw=1.3,
            style="<|-|>")
    d.arrow(20, 34.5, 80, 34.5, color=P["accent"], lw=1.8)
    d.text(30, 32.4, "미디어 P2P", size=8, color=P["accent"])

    # ── 아래: Video Streams ──
    d.box(2, 3, 96, 18, P["gray"])
    d.text(4, 18.8, "KVS Video Streams — 수집·저장·재생", size=9.5,
           weight="bold", ha="left")
    d.box(5, 5.5, 15, 9, P["green"])
    d.text(12.5, 10, "디바이스\n(Producer SDK\n· kvssink)", size=8)
    d.box(32, 6, 24, 8, P["brown"])
    d.text(44, 10, "Kinesis Video Stream\n(프래그먼트 · 보존 기간)", size=8.5)
    d.box(68, 5.5, 27, 9, P["blue"])
    d.text(81.5, 10, "HLS · DASH 재생\nGetMedia · GetImages", size=8.5)
    d.arrow(20, 10, 32, 10, color=P["accent"], lw=1.8)
    d.text(26, 12.2, "PutMedia", size=7.5, color=P["dim"])
    d.arrow(56, 10, 68, 10, color=P["accent"], lw=1.8)

    # ── 연결 고리: WebRTC 인제스트 ──
    d.arrow(50, 37, 44, 14, color=P["orange"], lw=1.8, ls=(0, (5, 3)))
    d.ax.text(62, 25.5, "WebRTC 인제스트 (저장 세션)\nUpdateMediaStorageConfiguration"
              " · JoinStorageSession", fontsize=8, color=P["orange"],
              ha="center", va="center", zorder=5,
              bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.5))


diagram("17-kvs-family", draw, w=12.5, h=5.5, ymax=50)

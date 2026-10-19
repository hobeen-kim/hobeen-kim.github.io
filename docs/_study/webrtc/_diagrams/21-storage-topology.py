"""CH21 §2 기본(P2P) 모드 vs 저장 모드 — 미디어가 흐르는 경로 비교 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    # ── 왼쪽: 기본 모드 ──
    d.box(1, 2, 46.5, 50, P["bg"], ec=P["edge"], lw=1.0)
    d.text(3, 49.5, "기본 모드 (P2P)", size=10, weight="bold", ha="left")

    d.box(14, 39, 20, 7, P["purple"])
    d.text(24, 42.5, "시그널링 채널", size=9.2, weight="bold")

    d.box(3, 17, 13, 10, P["green"])
    d.text(9.5, 23.2, "디바이스", size=9.5, weight="bold")
    d.text(9.5, 19.6, "(master)", size=8, color=P["dim"])

    vys = [31, 20, 9]
    for i, vy in enumerate(vys):
        d.box(33, vy - 3.5, 13, 7, P["blue"])
        d.text(39.5, vy, f"viewer {i + 1}", size=8.8)
        d.arrow(16.2, 22, 32.8, vy, color=P["accent"], lw=1.6)
    d.arrow(9.5, 27.2, 15, 38.8, color=P["orange"], ls="--", lw=1.2, style="<|-|>")
    d.arrow(39.5, 34.7, 33, 38.8, color=P["orange"], ls="--", lw=1.2, style="<|-|>")
    d.text(24, 34.5, "SDP · ICE만", size=8, color=P["orange"])
    d.text(24, 4.5, "업링크 = viewer 수 × 비트레이트", size=8.2, color=P["dim"])

    # ── 오른쪽: 저장 모드 ──
    d.box(52.5, 2, 46.5, 50, P["bg"], ec=P["accent"], lw=1.2)
    d.text(54.5, 49.5, "저장 모드 (WebRTC ingestion)", size=10, weight="bold", ha="left")

    d.box(64, 39, 20, 7, P["purple"])
    d.text(74, 42.5, "시그널링 채널", size=9.2, weight="bold")

    d.box(54, 19, 11, 10, P["green"])
    d.text(59.5, 25.2, "디바이스", size=9.2, weight="bold")
    d.text(59.5, 21.6, "(master)", size=8, color=P["dim"])

    d.box(70, 18, 13, 12, P["gray"], ec=P["accent"], lw=1.6)
    d.text(76.5, 25.6, "storage", size=9.2, weight="bold")
    d.text(76.5, 22.2, "세션 (AWS)", size=8.5)

    d.arrow(65.2, 24, 69.8, 24, color=P["accent"], lw=2.2)
    d.text(67.4, 31.5, "H.264+Opus\n1회 업링크", size=7.6, color=P["accent"])

    for i, vy in enumerate([35, 26]):
        d.box(87, vy - 3, 11, 6, P["blue"])
        d.text(92.5, vy, f"viewer {i + 1}", size=8.3)
        d.arrow(83.2, 25 + i * 0.0, 86.8, vy, color=P["accent"], lw=1.4)
    d.text(92.5, 20.6, "최대 3명", size=7.8, color=P["dim"])

    d.box(84, 6, 14, 8, P["brown"])
    d.text(91, 11.2, "Video Stream", size=8.6, weight="bold")
    d.text(91, 8.2, "H.264 + AAC", size=7.6, color=P["dim"])
    d.arrow(80, 17.8, 86, 14.2, color=P["violet"], lw=1.5)
    d.text(70.5, 9.5, "HLS/DASH로\n다수 시청", size=7.8, color=P["violet"])
    d.arrow(83.8, 9.5, 77.5, 9.5, color=P["violet"], lw=1.1, ls="--")

    d.arrow(59.5, 29.2, 66, 38.8, color=P["orange"], ls="--", lw=1.2, style="<|-|>")
    d.arrow(76.5, 30.2, 75, 38.8, color=P["orange"], ls="--", lw=1.2, style="<|-|>")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="미디어 (SRTP)"),
        Line2D([0], [0], color=P["orange"], lw=1.4, ls="--", label="시그널링"),
        Line2D([0], [0], color=P["violet"], lw=1.4, label="저장·재생"),
    ], loc="lower left", anchor=(0.52, 0.03))


diagram("21-storage-topology", draw, w=13, h=6.4, ymax=54)

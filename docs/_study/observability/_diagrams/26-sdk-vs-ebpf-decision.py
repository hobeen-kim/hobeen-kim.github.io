"""CH26 SDK vs eBPF 선택 결정 트리 (light/dark PNG)."""
from matplotlib.patches import Polygon
from _common import diagram


def draw(d):
    P = d.P

    def diamond(cx, cy, w, h, fc, ec=None, lw=1.8):
        pts = [(cx, cy + h / 2), (cx + w / 2, cy),
               (cx, cy - h / 2), (cx - w / 2, cy)]
        d.ax.add_patch(Polygon(pts, closed=True, facecolor=fc,
                               edgecolor=ec or P["orange"], linewidth=lw, zorder=3))

    # Q1
    diamond(30, 45, 34, 15, P["brown"])
    d.text(30, 45, "모든 워크로드에\n기본 CPU 가시성\n필요?", size=9.5, weight="bold")

    # eBPF (Q1 예)
    d.box(60, 40, 30, 10, P["purple"], ec=P["accent"], lw=1.8)
    d.text(75, 46.4, "eBPF (DaemonSet)", size=11.5, weight="bold")
    d.text(75, 42.8, "전역 기본 커버리지", size=9, color=P["dim"])

    d.arrow(47, 45, 60, 45, color=P["accent"], lw=2.2)
    d.text(53.5, 46.8, "예", size=10, color=P["accent"], weight="bold")

    # Q2
    diamond(30, 24, 34, 15, P["brown"])
    d.text(30, 24, "메모리/lock 프로파일\n요청 단위 태깅\n필요?", size=9.5, weight="bold")

    d.arrow(30, 37.5, 30, 31.5, color=P["dim"], lw=2.0)
    d.text(33.5, 34.5, "아니오", size=9, color=P["dim"], weight="bold", ha="left")

    # eBPF -> Q2 (계층 조합)
    d.arrow(75, 40, 47, 26, color=P["violet"], lw=1.8, ls=(0, (5, 3)))
    d.text(63, 35, "그 위에 추가 판단", size=8, color=P["violet"], style="italic")

    # SDK 추가 (Q2 예)
    d.box(60, 19, 30, 9, P["green"], ec=P["accent"], lw=1.8)
    d.text(75, 25, "언어별 SDK 추가", size=11.5, weight="bold")
    d.text(75, 21.6, "요청 단위 태깅 · 풍부한 타입", size=8.5, color=P["dim"])

    d.arrow(47, 24, 60, 24, color=P["accent"], lw=2.2)
    d.text(53.5, 25.8, "예", size=10, color=P["accent"], weight="bold")

    # eBPF만으로 충분 (Q2 아니오)
    d.box(15, 6, 30, 8, P["gray"], ec=P["edge"], lw=1.4)
    d.text(30, 11, "eBPF만으로 충분", size=10.5, weight="bold")
    d.text(30, 8.2, "추가 계측 불필요", size=8, color=P["dim"])

    d.arrow(30, 16.5, 30, 14, color=P["dim"], lw=2.0)
    d.text(33.5, 15.5, "아니오", size=9, color=P["dim"], weight="bold", ha="left")

    # eBPF + SDK 조합 (최종)
    d.box(60, 6, 30, 8, P["gray"], ec=P["accent"], lw=1.9)
    d.text(75, 11, "eBPF + SDK 조합", size=11, weight="bold", color=P["accent"])
    d.text(75, 8.2, "전역 커버리지 + 핵심 서비스 심층", size=8, color=P["dim"])

    d.arrow(75, 19, 75, 14, color=P["accent"], lw=2.0)


diagram("26-sdk-vs-ebpf-decision", draw, w=12, h=6.5, ymax=52)

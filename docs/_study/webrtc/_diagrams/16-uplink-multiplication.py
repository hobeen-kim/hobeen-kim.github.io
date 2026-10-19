"""CH16 §3 KVS P2P에서 뷰어 수만큼 늘어나는 디바이스 업링크 — 구조 비교 + 필요 업링크 막대 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ── 왼쪽 위: KVS P2P ──
    d.box(1, 31, 50, 24, P["gray"])
    d.text(3, 52.6, "KVS WebRTC (P2P)", size=10, weight="bold", ha="left")
    d.box(4, 37, 12, 9, P["green"])
    d.text(10, 41.5, "디바이스\n(인코더 1개)", size=8.5)
    for i, y in enumerate([48, 41.5, 35]):
        d.box(39, y - 2.2, 10, 4.4, P["blue"])
        d.text(44, y, f"뷰어 {i + 1}", size=8.5)
        d.arrow(16, 41.5 + (i - 1) * -2.2, 39, y, color=P["accent"], lw=1.8)
    d.text(27.5, 33.2, "PeerConnection 3개 · 업링크 2 Mbps × 3 = 6 Mbps",
           size=8, color=P["orange"])

    # ── 왼쪽 아래: SFU 계열 ──
    d.box(1, 3, 50, 25, P["gray"])
    d.text(3, 25.6, "SFU 계열 (Chime SDK · IVS · 직접 구축)", size=10,
           weight="bold", ha="left")
    d.box(4, 10.5, 12, 9, P["green"])
    d.text(10, 15, "디바이스", size=8.5)
    d.box(23, 12, 9, 6, P["purple"], ec=P["accent"], lw=1.5)
    d.text(27.5, 15, "SFU", size=9, weight="bold")
    d.arrow(16, 15, 23, 15, color=P["accent"], lw=1.8)
    for i, y in enumerate([21, 15, 9]):
        d.box(39, y - 2.2, 10, 4.4, P["blue"])
        d.text(44, y, f"뷰어 {i + 1}", size=8.5)
        d.arrow(32, 15 + (1 - i) * 1.5, 39, y, color=P["orange"], lw=1.6)
    d.text(27.5, 5.2, "업링크 2 Mbps × 1 · 복제는 서버 몫", size=8,
           color=P["orange"])

    # ── 오른쪽: 뷰어 수별 필요 업링크 (2 Mbps 스트림 가정) ──
    bx0, by0, bw = 59, 8, 2.5
    scale = 2.0  # 1 Mbps = 2 단위
    d.ax.plot([bx0 - 1, 89], [by0, by0], color=P["edge"], lw=1.0)
    for n in range(1, 11):
        x = bx0 + (n - 1) * 3.0
        h = 2 * n * scale
        d.box(x, by0, bw, h, P["blue"], ec=P["accent"], lw=1.0, r=0.005)
        d.text(x + bw / 2, by0 - 2, str(n), size=8, color=P["dim"])
        if n in (1, 3, 5, 10):
            d.text(x + bw / 2, by0 + h + 1.4, f"{2 * n}", size=8,
                   color=P["text"])
    d.text(bx0 + 14.5, by0 - 5, "채널의 동시 뷰어 수 (기본 한도 10)", size=8.5,
           color=P["dim"])
    d.text(bx0 - 1, 52, "필요 업링크 (Mbps, 스트림당 2 Mbps 가정)", size=8.5,
           color=P["dim"], ha="left")
    # 가정 업링크선
    ly = by0 + 6 * scale
    d.ax.plot([bx0 - 1, 89], [ly, ly], color=P["orange"], lw=1.3,
              ls=(0, (5, 3)))
    d.text(90, ly, "예: 현장 LTE\n업링크 여유\n6 Mbps (가정)", size=8,
           color=P["orange"], ha="left")


diagram("16-uplink-multiplication", draw, w=14, h=7, ymax=56)

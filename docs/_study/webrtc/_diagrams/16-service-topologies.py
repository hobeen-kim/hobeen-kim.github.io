"""CH16 §1 AWS 관리형 WebRTC 세 서비스의 미디어 경로 — KVS P2P / Chime SFU / IVS Stage (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    Y0 = 5

    def panel(x, title, sub):
        d.box(x, Y0, 31, 38, P["gray"])
        d.text(x + 15.5, Y0 + 35.4, title, size=11, weight="bold")
        d.text(x + 15.5, Y0 + 32.6, sub, size=8, color=P["dim"])

    def node(cx, cy, label, fc, w=9, h=4.6, size=8.5):
        d.box(cx - w / 2, cy - h / 2, w, h, fc)
        d.text(cx, cy, label, size=size)

    # ── KVS WebRTC ──
    panel(1, "KVS WebRTC", "시그널링만 관리형, 미디어는 P2P")
    d.box(8.5, 28.2, 16, 4.6, P["chip"], ec=P["violet"], lw=1.3)
    d.text(16.5, 30.5, "시그널링 채널", size=8.5, color=P["violet"])
    node(7.5, 15, "디바이스\n(Master)", P["green"], w=10, h=6)
    vy = [24, 16.5, 9]
    for y in vy:
        node(26.5, y, "뷰어", P["blue"], w=7, h=4)
    # 시그널링 점선
    d.arrow(9, 18, 12, 28.2, color=P["violet"], lw=1.1, ls="--", style="-")
    d.arrow(24.5, 28.2, 26.5, 26, color=P["violet"], lw=1.1, ls="--", style="-")
    # 미디어: 뷰어마다 별도 업링크
    d.arrow(12.5, 16.5, 23, 23.5, color=P["accent"], lw=1.6)
    d.arrow(12.5, 15.4, 23, 16.5, color=P["accent"], lw=1.6)
    d.arrow(12.5, 14, 23, 9.5, color=P["accent"], lw=1.6)
    d.text(16.5, Y0 + 2.2, "뷰어 N명 = 업링크 N개", size=8, color=P["dim"])

    # ── Chime SDK ──
    panel(34.5, "Amazon Chime SDK", "SFU(미디어 서비스) 경유 회의")
    d.box(44.5, 16.5, 11, 6.5, P["purple"], ec=P["accent"], lw=1.6)
    d.text(50, 19.75, "미디어 서비스\n(SFU)", size=8.5, weight="bold")
    for (cx, cy) in [(40.5, 28), (59.5, 28), (40.5, 10), (59.5, 10)]:
        node(cx, cy, "참석자", P["blue"], w=8, h=4)
        tx = 46 if cx < 50 else 54
        ty = 23 if cy > 20 else 16.5
        sy = cy - 2 if cy > 20 else cy + 2
        d.arrow(cx, sy, tx, ty, color=P["accent"], lw=1.4, style="<|-|>")
    d.text(50, Y0 + 2.2, "참석자당 업 1 · 다운 구독 수", size=8, color=P["dim"])

    # ── IVS Real-Time ──
    panel(68, "Amazon IVS Real-Time", "Stage에 publish / subscribe")
    d.box(78.5, 16.5, 11, 6.5, P["brown"], ec=P["accent"], lw=1.6)
    d.text(84, 19.75, "Stage", size=9, weight="bold")
    node(73.5, 27, "호스트", P["green"], w=8, h=4)
    node(73.5, 11, "호스트", P["green"], w=8, h=4)
    d.arrow(76, 25, 79.5, 23, color=P["accent"], lw=1.5)
    d.arrow(76, 13, 79.5, 16.5, color=P["accent"], lw=1.5)
    for cy in (27, 19.75, 12.5):
        node(94.5, cy, "시청자", P["blue"], w=7, h=3.6, size=8)
    d.arrow(89.5, 21.5, 91, 26, color=P["orange"], lw=1.4)
    d.arrow(89.5, 19.75, 91, 19.75, color=P["orange"], lw=1.4)
    d.arrow(89.5, 18, 91, 13.5, color=P["orange"], lw=1.4)
    d.text(83.5, Y0 + 2.2, "publisher ≤12 · subscriber 다수", size=8, color=P["dim"])

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["violet"], lw=1.6, ls="--", label="시그널링"),
        Line2D([0], [0], color=P["accent"], lw=2.2, label="송신 미디어"),
        Line2D([0], [0], color=P["orange"], lw=2.2, label="서버가 복제한 수신 미디어"),
    ], loc="lower center", bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=8,
        framealpha=0.0, labelcolor=P["dim"])


diagram("16-service-topologies", draw, w=14, h=6, ymax=44)

"""CH12 §2 Simulcast vs SVC — SFU가 수신자별로 계층을 고르는 방식 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    cols = [P["accent"], P["orange"], P["violet"]]

    # ── Simulcast ─────────────────────────────
    d.box(1, 31, 98, 27, P["gray"])
    d.text(3, 55.6, "Simulcast — 독립 스트림 3개 (rid f / h / q, SSRC 각각)",
           size=10, weight="bold", ha="left")
    d.box(4, 37, 14, 13, P["blue"])
    d.text(11, 43.5, "송신자\n(인코딩 3회)", size=9.5)
    layers = [("f · 1280×720 · 1.5 Mbps", 47.5),
              ("h · 640×360 · 500 kbps", 43.5),
              ("q · 320×180 · 150 kbps", 39.5)]
    for (lbl, y), c in zip(layers, cols):
        d.arrow(18, y, 44, y, color=c, lw=1.7)
        d.text(31, y + 1.3, lbl, size=7.8, color=c)
    d.box(44, 36, 14, 15, P["purple"], ec=P["accent"], lw=1.6)
    d.text(51, 43.5, "SFU\n(스트림 선택)", size=9.5, weight="bold")
    recv = [("PC 운영자 (광대역)", 46.5, "f"),
            ("모바일 (LTE)", 41.2, "h"),
            ("썸네일 그리드", 35.9, "q")]
    for (lbl, y, tag), c in zip(recv, cols):
        d.box(72, y, 24, 4.4, P["chip"])
        d.text(84, y + 2.2, lbl, size=8.8)
        d.arrow(58, y + 2.2, 72, y + 2.2, color=c, lw=1.6)
        d.text(65, y + 3.4, tag, size=8, color=c, weight="bold")

    # ── SVC ───────────────────────────────────
    d.box(1, 2, 98, 27, P["gray"])
    d.text(3, 26.6, "SVC — 계층 스트림 1개 (예: L3T3, 상위 계층이 하위 계층을 참조)",
           size=10, weight="bold", ha="left")
    d.box(4, 8, 14, 13, P["blue"])
    d.text(11, 14.5, "송신자\n(인코딩 1회)", size=9.5)
    d.box(22.5, 7.2, 17, 14.6, P["chip"], ec=P["accent"], lw=1.2)
    chips = [("L2 · 1280×720", 17.4), ("L1 · 640×360", 13.4), ("L0 · 320×180", 9.4)]
    for (lbl, y), c in zip(chips, cols):
        d.box(24, y - 1.5, 14, 3.2, P["blue"], ec=c, lw=1.4)
        d.text(31, y + 0.1, lbl, size=8)
    d.text(31, 5.2, "단일 SSRC", size=7.8, color=P["dim"])
    d.arrow(18, 14.5, 22.5, 14.5, color=P["accent"], lw=1.7)
    d.arrow(39.5, 14.5, 44, 14.5, color=P["accent"], lw=1.7)
    d.box(44, 7, 14, 15, P["purple"], ec=P["accent"], lw=1.6)
    d.text(51, 14.5, "SFU\n(상위 계층 드롭)", size=9.5, weight="bold")
    recv2 = [("PC: L0 + L1 + L2", 17.5), ("모바일: L0 + L1", 12.2), ("썸네일: L0", 6.9)]
    for (lbl, y), c in zip(recv2, cols):
        d.box(72, y, 24, 4.4, P["chip"])
        d.text(84, y + 2.2, lbl, size=8.8)
        d.arrow(58, y + 2.2, 72, y + 2.2, color=c, lw=1.6)


diagram("12-simulcast-svc", draw, w=13, h=7.6, ymax=59)

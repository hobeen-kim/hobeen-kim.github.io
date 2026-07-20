"""CH16 §6 ISB 메시지 흐름 — 서버(버튼)가 브로드캐스트, 모든 작업기가 안전 상태로."""
from _common import diagram


def draw(d):
    P = d.P

    # ISB 서버
    d.box(2, 14, 24, 16, P["brown"])
    d.text(14, 26, "ISB (버튼)", size=10.5, weight="bold")
    d.text(14, 20.5, "ShortcutButtonInterface\n(internalECU, true)\nupdate() ≥ 50 ms", size=8.4)

    # 버스
    d.box(30, 18, 34, 8, P["chip"])
    d.text(47, 23.4, "PGN 64770 (0xFD02)  브로드캐스트", size=9, color=P["dim"])
    d.text(47, 20.2, "StopAllImplementOperationsState  주기 1000 ms", size=8.2, color=P["dim"])
    d.arrow(26, 22, 30, 22, color=P["orange"])

    # 수신 작업기들
    for i, y in enumerate((28, 15.5, 3)):
        d.box(70, y, 28, 10, P["green"])
        d.text(84, y + 6.6, f"작업기 {i + 1}", size=9, weight="bold")
        d.text(84, y + 3.2, "get_state() / 리스너\n→ 즉시 안전 상태", size=8.2, color=P["dim"])
        d.arrow(64, 22, 70, y + 5, color=P["orange"], lw=1.4)

    d.text(47, 14.5, "수신 측 update() ≥ 100 ms · 3000 ms 무수신 → stale",
           size=8.4, color=P["dim"])


diagram("16-isb-flow", draw, w=13, h=5.0, ymax=40)

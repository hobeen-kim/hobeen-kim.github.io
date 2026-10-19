"""CH11 §4 원격 제어 명령 채널 — 시퀀스 필터와 워치독 안전정지 타임라인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    ys, yr = 38, 18          # 송신 레인 / 수신 레인
    x0, x1 = 14, 97

    # 레인
    d.text(7, ys, "운영자\n(50Hz 송신)", size=9, weight="bold")
    d.text(7, yr, "디바이스\n(제어 루프)", size=9, weight="bold")
    for y in (ys, yr):
        d.ax.plot([x0, x1], [y, y], color=P["edge"], lw=1.2, zorder=1)

    # 메시지: (seq, 송신 x, 수신 x 또는 None)
    msgs = [
        (101, 16, 20),
        (102, 23, 27),
        (103, 30, None),     # 손실
        (104, 37, 41),
        (105, 44, 55.5),     # 지연 → 106 뒤에 도착
        (106, 51, 51.5),
        (107, 61, None),     # 링크 끊김 이후
        (108, 68, None),
    ]
    for seq, xs, xr in msgs:
        d.box(xs - 2.6, ys + 1.2, 5.2, 4, P["blue"])
        d.text(xs, ys + 3.2, str(seq), size=8)
        if xr is None:
            d.arrow(xs, ys, xs + 2.5, ys - 7, color=P["edge"], lw=1.2, ls="--", style="-")
            d.text(xs + 3.3, ys - 7.8, "X", size=9.5, color=P["orange"], weight="bold")
            continue
        color = P["orange"] if seq == 105 else P["accent"]
        d.arrow(xs, ys, xr, yr, color=color, lw=1.5)
        mark = "폐기" if seq == 105 else "적용"
        d.text(xr, yr - 2.6, mark, size=7.8, color=color, weight="bold")

    d.text(30.5, 27.5, "손실:\n재전송 안 함", size=7.6, color=P["dim"])
    d.text(62, 26.5, "105 지연 도착\n(seq ≤ 106) → 폐기", size=7.6, color=P["orange"])
    d.text(57, 47, "링크 끊김", size=8, color=P["violet"], weight="bold")
    d.ax.plot([57, 57], [16, 45.5], color=P["violet"], lw=1.2, ls=(0, (3, 3)), zorder=1)

    # 디바이스 상태 바
    states = [
        (14, 51.5, P["green"], "주행 (마지막 유효 명령 적용)"),
        (51.5, 67, P["brown"], "감속"),
        (67, 97, P["purple"], "안전정지 · 재무장 대기"),
    ]
    for a, b, fc, label in states:
        d.box(a, 4, b - a, 5.5, fc)
        d.text((a + b) / 2, 6.75, label, size=8.3, weight="bold")

    # 워치독 구간
    d.arrow(51.5, 12.5, 67, 12.5, color=P["violet"], lw=1.3, style="<|-|>")
    d.text(59.5, 14.2, "워치독 300ms", size=7.8, color=P["violet"])
    d.text(82, 14.2, "새 세션 · 데드맨 재입력 전엔\n명령 무시", size=7.8, color=P["dim"])


diagram("11-control-watchdog", draw, w=13, h=5.6, ymax=48)

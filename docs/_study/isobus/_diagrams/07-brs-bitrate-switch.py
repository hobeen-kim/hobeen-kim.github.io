"""CH7 §3 BRS 비트 기준 CAN FD 비트레이트 전환 — Arbitration(500kbps) -> BRS -> Data(2~8Mbps) -> EOF(500kbps 복귀) (light/dark PNG)."""
from _common import diagram

# 구간 x 범위 (원본 gantt 비율 4:6:2 반영)
ARB_X, ARB_W = 5, 30
DATA_X, DATA_W = ARB_X + ARB_W, 45
EOF_X, EOF_W = DATA_X + DATA_W, 15

BAND_Y, BAND_H = 22, 12
BRS_W = 4


def draw(d):
    P = d.P
    ax = d.ax

    # ── 구간 배경 밴드 ──
    d.box(ARB_X, BAND_Y, ARB_W, BAND_H, P["gray"], ec=P["edge"], lw=1.3)
    d.box(DATA_X, BAND_Y, DATA_W, BAND_H, P["blue"], ec=P["accent"], lw=1.6)
    d.box(EOF_X, BAND_Y, EOF_W, BAND_H, P["gray"], ec=P["edge"], lw=1.3)

    # ── 비트 틱: 저속 구간은 성기게, 고속 구간은 촘촘하게 ──
    def ticks(x0, x1, step, color, alpha=0.8):
        x = x0
        while x <= x1:
            ax.plot([x, x], [BAND_Y + 1.2, BAND_Y + BAND_H - 1.2],
                    color=color, lw=0.8, alpha=alpha, zorder=3)
            x += step

    ticks(ARB_X + 1.5, ARB_X + ARB_W - 1.5, 5.0, P["dim"])
    ticks(DATA_X + 1.2, DATA_X + DATA_W - 1.2, 1.1, P["accent"], alpha=0.65)
    ticks(EOF_X + 1.2, EOF_X + EOF_W - 1.2, 5.0, P["dim"])

    # ── BRS 전환 비트 마커 ──
    brs_x = ARB_X + ARB_W - BRS_W / 2
    d.box(brs_x, BAND_Y - 2.5, BRS_W, BAND_H + 5, P["chip"], ec=P["accent"], lw=1.8, r=0.06)
    d.text(brs_x + BRS_W / 2, BAND_Y + BAND_H + 1.0, "BRS", size=9, weight="bold",
           color=P["accent"])
    d.text(brs_x + BRS_W / 2, BAND_Y + BAND_H * 0.5, "1", size=11, weight="bold",
           color=P["accent"])
    d.arrow(brs_x + BRS_W / 2, BAND_Y - 3.0, brs_x + BRS_W / 2, BAND_Y - 6.0,
            color=P["accent"], lw=1.4)
    d.text(brs_x + BRS_W / 2, BAND_Y - 8.2, "전환 시점", size=8.8, color=P["accent"])

    # ── 구간 제목 (위) ──
    d.text(ARB_X + ARB_W / 2, BAND_Y + BAND_H + 4.5, "Arbitration phase",
           size=10.5, weight="bold")
    d.text(DATA_X + DATA_W / 2, BAND_Y + BAND_H + 4.5, "Data phase",
           size=10.5, weight="bold", color=P["accent"])
    d.text(DATA_X + DATA_W / 2, BAND_Y + BAND_H + 1.0, "고속 전송 구간",
           size=8.8, color=P["accent"])
    d.text(EOF_X + EOF_W / 2, BAND_Y + BAND_H + 4.5, "EOF",
           size=10.5, weight="bold")
    d.text(EOF_X + EOF_W / 2, BAND_Y + BAND_H + 1.0, "표준 복귀",
           size=8.8, color=P["dim"])

    # ── 비트레이트 (아래) ──
    d.text(ARB_X + ARB_W / 2, BAND_Y - 4.5, "500 kbps", size=9.5, color=P["dim"])
    d.text(DATA_X + DATA_W / 2, BAND_Y - 4.5, "2~8 Mbps", size=9.5,
           color=P["accent"], weight="bold")
    d.text(EOF_X + EOF_W / 2, BAND_Y - 4.5, "500 kbps", size=9.5, color=P["dim"])


diagram("07-brs-bitrate-switch", draw, w=13, h=5.6, xmax=100, ymax=42)

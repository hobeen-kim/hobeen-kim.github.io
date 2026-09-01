"""CH5 §3 29bit ID 중재 비트 비교 — 메시지A(0x0CF00400) vs 메시지B(0x0CFEEE00), PF 필드에서 승부 결정 (light/dark PNG).

검산 (29bit = Priority3 + EDP1 + DP1 + PF8 + PS8 + SA8):
  A 0x0CF00400 -> 011 0 0 11110000 00000100 00000000
  B 0x0CFEEE00 -> 011 0 0 11111110 11101110 00000000
  Priority/EDP/DP 동점, PF 5번째 비트(인덱스4)에서 A=0, B=1 -> A 승리
"""
from _common import diagram

PF_A = "11110000"
PF_B = "11111110"
DIVERGE_IDX = 4  # PF 8비트 중 0-indexed 발산 위치 (A=0, B=1)

# x 레이아웃
LABEL_X, LABEL_W = 1, 15
P_X, P_W = 17, 8
EDP_X, EDP_W = 26, 5
DP_X, DP_W = 32, 5
PF_X, PF_CELL_W = 38, 3  # 8칸
PS_X, PS_W = 63, 16
SA_X, SA_W = 80, 16

ROW_A_Y, ROW_B_Y, ROW_H = 32, 17, 9
HEADER_Y = 44


def pf_cell_x(i):
    return PF_X + i * PF_CELL_W


def draw(d):
    P = d.P

    # ── 그룹 헤더 라벨 ──
    d.text(P_X + P_W / 2, HEADER_Y, "Priority(3)", size=9.5, color=P["dim"])
    d.text(EDP_X + EDP_W / 2, HEADER_Y, "EDP", size=9.5, color=P["dim"])
    d.text(DP_X + DP_W / 2, HEADER_Y, "DP", size=9.5, color=P["dim"])
    d.text(PF_X + PF_CELL_W * 8 / 2, HEADER_Y, "PF(8)", size=9.5, color=P["dim"])
    d.text(PS_X + PS_W / 2, HEADER_Y, "PS(8)", size=9.5, color=P["dim"])
    d.text(SA_X + SA_W / 2, HEADER_Y, "SA(8)", size=9.5, color=P["dim"])

    # PF 칸 위 비트 인덱스 (칸 색과 겹치지 않도록 박스 바깥 위쪽에 배치)
    for i in range(8):
        d.text(pf_cell_x(i) + PF_CELL_W / 2, ROW_A_Y + ROW_H + 1.6, str(i),
               size=7, color=P["dim"])

    rows = [
        (ROW_A_Y, "메시지A", "0x0CF00400", PF_A, False),
        (ROW_B_Y, "메시지B", "0x0CFEEE00", PF_B, True),
    ]

    for y, name, idhex, pf_bits, is_loser in rows:
        # 행 라벨
        d.box(LABEL_X, y, LABEL_W, ROW_H, P["chip"], ec=P["edge"], lw=1.0)
        d.text(LABEL_X + LABEL_W / 2, y + ROW_H * 0.62, name, size=10, weight="bold")
        d.text(LABEL_X + LABEL_W / 2, y + ROW_H * 0.28, idhex, size=8.3, color=P["dim"])

        # Priority / EDP / DP — 동점 (녹색)
        d.box(P_X, y, P_W, ROW_H, P["green"], ec=P["edge"], lw=1.0)
        d.text(P_X + P_W / 2, y + ROW_H / 2, "011", size=10.5)

        d.box(EDP_X, y, EDP_W, ROW_H, P["green"], ec=P["edge"], lw=1.0)
        d.text(EDP_X + EDP_W / 2, y + ROW_H / 2, "0", size=10.5)

        d.box(DP_X, y, DP_W, ROW_H, P["green"], ec=P["edge"], lw=1.0)
        d.text(DP_X + DP_W / 2, y + ROW_H / 2, "0", size=10.5)

        # PF — 비트별 칸
        for i, bit in enumerate(pf_bits):
            cx = pf_cell_x(i)
            if i < DIVERGE_IDX:
                fc = P["green"]
                alpha = 1.0
            elif i == DIVERGE_IDX:
                fc = P["orange"] if is_loser else P["accent"]
                alpha = 1.0
            else:
                fc = P["gray"]
                alpha = 0.35 if is_loser else 0.7
            d.box(cx, y, PF_CELL_W, ROW_H, fc, ec=P["edge"], lw=1.0, alpha=alpha)
            tcolor = P["text"]
            if i > DIVERGE_IDX and is_loser:
                tcolor = P["dim"]
            d.text(cx + PF_CELL_W / 2, y + ROW_H / 2, bit, size=10.5, color=tcolor)

        # PS / SA — 이미 승부가 갈려 비교되지 않음 (옅게)
        ps_val = "00000100" if not is_loser else "11101110"
        sa_val = "00000000"
        for gx, gw, val in ((PS_X, PS_W, ps_val), (SA_X, SA_W, sa_val)):
            d.box(gx, y, gw, ROW_H, P["gray"], ec=P["edge"], lw=1.0, alpha=0.35)
            d.text(gx + gw / 2, y + ROW_H / 2, val, size=9.5, color=P["dim"])

    # 발산 지점 강조 화살표 + 라벨 (두 행 사이)
    div_cx = pf_cell_x(DIVERGE_IDX) + PF_CELL_W / 2
    d.arrow(div_cx, ROW_A_Y - 0.4, div_cx, ROW_B_Y + ROW_H + 0.4,
            color=P["accent"], lw=1.6, style="-")
    d.text(div_cx + 9, (ROW_A_Y + ROW_B_Y + ROW_H) / 2, "A=0, B=1\nA 승리",
           size=9.5, color=P["accent"], weight="bold", ha="left")


diagram("05-arbitration-bit-compare", draw, w=14, h=6.6, xmax=100, ymax=50)

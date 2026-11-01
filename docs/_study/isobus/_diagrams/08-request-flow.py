"""CH08 §5 J1939 통신 흐름 예시: 브로드캐스트, 요청, 응답의 시간 순서 (light/dark PNG)."""
from _common import diagram

COLS = {
    "ENG": (12, "엔진 ECU\n(SA=0x00)", "blue"),
    "BUS": (40, "J1939 버스", "gray"),
    "DASH": (66, "계기판\n(SA=0x17)", "green"),
    "DIAG": (90, "진단 도구\n(SA=0xF9)", "purple"),
}


def draw(d):
    P = d.P
    top = 62
    for x, label, color in COLS.values():
        d.box(x - 8, top, 16, 7, P[color])
        d.text(x, top + 3.5, label, size=8.8)
        d.ax.plot([x, x], [2, top], color=P["edge"], lw=1.0, ls=(0, (2, 3)))

    def msg(src, dst, y, label, dashed=False, above=True):
        x1, x2 = COLS[src][0], COLS[dst][0]
        d.arrow(x1, y, x2, y, color=P["dim"] if dashed else P["accent"],
                ls="--" if dashed else "-", lw=1.6)
        ty = y + 2.0 if above else y - 2.0
        lx = (x1 + x2) / 2
        if "DIAG" in (src, dst):
            lx = (COLS["DASH"][0] + COLS["DIAG"][0]) / 2
        d.text(lx, ty, label, size=8.2,
               color=P["dim"] if dashed else P["text"])

    msg("ENG", "BUS", 56, "PGN 65262 (Engine Temp)\nSA=0x00, 브로드캐스트")
    msg("BUS", "DASH", 50, "수신 → 수온 게이지 표시", dashed=True)
    msg("BUS", "DIAG", 45, "수신 → 로그 기록", dashed=True)

    msg("DIAG", "BUS", 36, "PGN 59904 (Request PGN)\nDA=0x00, SA=0xF9")
    msg("BUS", "ENG", 29, "요청 수신 →\nPGN 65262 응답", dashed=True)

    msg("ENG", "BUS", 20, "PGN 65262 응답\n(SA=0x00)")
    msg("BUS", "DASH", 13, "수신", dashed=True)
    msg("BUS", "DIAG", 8, "수신", dashed=True)


diagram("08-request-flow", draw, w=10.5, h=6.6, xmax=100, ymax=70)

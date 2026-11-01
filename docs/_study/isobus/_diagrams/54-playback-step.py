"""54장 4절: 재생 한 스텝의 메시지 여섯 개 (SCM ↔ SCC 순서도, light/dark PNG)."""
from _common import diagram

SCM_X, SCC_X = 19, 81

MESSAGES = [
    # (y, SCM→SCC?, bytes, meaning)
    (50, True, "95 01 02 04 00 FF FF FF", "1. SCMasterStatus: 시퀀스 0x02 Play back (전역)"),
    (42, True, "33 05 02 12 4C 1D 00 00", "2. 실행 명령: 히치(0x05) 상승(2), TAN 0x12, 값 7 500"),
    (34, False, "34 05 42 00 12 FF FF FF", "3. 실행 시작(01) 보고, TAN 0x12"),
    (26, True, "34 05 42 12 FF FF FF FF", "4. 시작 확인 (TAN은 Byte 4)"),
    (16, False, "34 05 82 00 12 FF FF FF", "5. 실행 완료(10) 보고"),
    (8, True, "34 05 82 12 FF FF FF FF", "6. 완료 확인"),
]


def draw(d):
    P = d.P

    for x, label, fc in ((SCM_X, "SCM", P["blue"]), (SCC_X, "SCC (3점 히치)", P["green"])):
        d.box(x - 11, 55, 22, 6.5, fc)
        d.text(x, 58.25, label, size=10.5)
        d.ax.plot([x, x], [55, 2.5], color=P["edge"], lw=1.1, ls=(0, (4, 3)), zorder=1)

    # 히치가 움직이는 동안
    d.box(SCC_X - 1, 16, 2, 26, P["green"], r=0.005)
    d.text(SCC_X + 2.6, 29, "히치\n상승 중", size=8.5, color=P["dim"], ha="left")

    for y, to_scc, data, meaning in MESSAGES:
        color = P["accent"] if to_scc else P["orange"]
        x1, x2 = (SCM_X + 0.6, SCC_X - 1.4) if to_scc else (SCC_X - 1.4, SCM_X + 0.6)
        d.arrow(x1, y, x2, y, color=color)
        d.ax.text(50, y + 1.9, data, fontsize=9.5, color=P["text"], ha="center", va="center",
                  family="monospace", zorder=5)
        d.text(50, y - 2.0, meaning, size=8.5, color=P["dim"])


diagram("54-playback-step", draw, w=12, h=7.4, xmax=100, ymax=62)

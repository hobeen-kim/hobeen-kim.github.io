"""CH17 §13 AUX-N(Type 2) 할당 시퀀스: 입력 유닛 준비, Preferred Assignment, VT 할당 처리, 상태 송신, 해제 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P
    IN, VT, FN = 12, 50, 88
    TOP = 66

    for x, name, col in [(IN, "AUX 입력 유닛\n(조이스틱)", P["brown"]),
                         (VT, "VT\n(function instance 0)", P["blue"]),
                         (FN, "기능 WS\n(작업기)", P["green"])]:
        d.box(x - 9, TOP, 18, 6.4, col, lw=1.4)
        d.text(x, TOP + 3.2, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [1.5, TOP], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", lx=None):
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=1.6)
        d.text(lx if lx is not None else (x1 + x2) / 2, y + 1.1, label, size=8, color=color)

    def bcast(y, label):
        d.arrow(IN, y, FN, y, color=P["violet"], lw=1.6)
        d.ax.plot([VT], [y], marker="o", ms=5, color=P["violet"], zorder=6)
        d.text((VT + FN) / 2, y + 1.1, label, size=8, color=P["violet"])

    bcast(61.5, "AUX Input Maintenance (Status=0, 100 ms)")
    hop(IN, VT, 57.5, "오브젝트 풀 업로드, End of Object Pool", P["accent"])
    hop(VT, IN, 54.0, "End of Object Pool response (오류 없음)", P["dim"], ls="--")
    bcast(50.0, "Maintenance (Status=1 Ready)")
    hop(FN, VT, 46.0, "Preferred Assignment command", P["accent"])
    hop(VT, FN, 42.5, "Preferred Assignment response", P["dim"], ls="--")

    d.box(VT - 11, 36.2, 22, 3.6, P["purple"], lw=1.2)
    d.text(VT, 38.0, "할당 처리 (충돌 검사)", size=8.5, weight="bold")

    hop(VT, IN, 32.5, "Status Type 2 Enable (enable)", P["accent"])
    hop(IN, VT, 29.0, "Enable response", P["dim"], ls="--")
    hop(VT, FN, 25.5, "Auxiliary Assignment Type 2 (14바이트)", P["accent"])
    hop(FN, VT, 22.0, "Assignment response (1 s 이내)", P["dim"], ls="--")
    bcast(18.0, "AUX Input Type 2 Status (최대 20 Hz)")

    d.ax.plot([3, 97], [14.6, 14.6], color=P["edge"], ls=(0, (2, 3)), lw=1.0)
    d.text(97, 13.2, "운전자가 할당 해제", size=8.5, color=P["orange"], ha="right")

    hop(VT, FN, 9.5, "Assignment Type 2 (NULL = 해제)", P["orange"])
    hop(VT, IN, 5.0, "Status Type 2 Enable (disable)", P["orange"])
    d.text(IN + 1.0, 2.6, "Status 송신 중단", size=8, color=P["dim"], ha="left")

    d.legend([
        Line2D([0], [0], color=P["violet"], lw=2.2, label="전역 브로드캐스트"),
        Line2D([0], [0], color=P["accent"], lw=2.2, label="명령"),
        Line2D([0], [0], color=P["dim"], lw=2.2, ls="--", label="응답"),
    ], loc="upper left", anchor=(0.005, 0.86), fontsize=8)


diagram("17-aux-assignment-sequence", draw, w=13.5, h=9.6, xmax=100, ymax=74)

"""CH13 Part 7 Annex D 작업기의 후방 히치 원격 제어 시퀀스 (light/dark PNG)."""
from _common import diagram

OP, TECU, IMP = 22, 54, 87

STEPS = [
    # (from, to, label, kind, phase)
    (TECU, IMP, "Tractor facility response (B.24.3)", "status", "기능 확인"),
    (IMP, TECU, "Required tractor facilities (B.24.4)", "cmd_opt", None),
    (TECU, IMP, "B.7 rear hitch 40 %, limit 001", "status", "초기화"),
    (IMP, TECU, "B.10 hitch cmd = 40 % (현재값 일치)", "cmd", None),
    (TECU, IMP, "B.7 limit 000 Not limited", "status", None),
    (IMP, TECU, "B.10 hitch cmd = 64 % (100 ms 반복)", "cmd", "원격 제어"),
    (OP, TECU, "캡에서 히치 수동 조작", "op", "운전자 개입"),
    (TECU, IMP, "B.7 limit 001, exit 000011", "status", None),
    (IMP, TECU, "B.10 hitch cmd = 현재 위치 (재일치)", "cmd", None),
    (TECU, IMP, "B.7 limit 000 Not limited", "status", None),
    (IMP, TECU, "B.10 hitch cmd = FF (Not requested)", "cmd", "반납"),
]


def draw(d):
    P = d.P
    top = 60
    lanes = [(OP, "운전자", P["gray"]), (TECU, "TECU", P["blue"]),
             (IMP, "작업기 (WSM·TC)", P["green"])]
    for x, name, col in lanes:
        d.box(x - 9, top, 18, 5, col)
        d.text(x, top + 2.5, name, size=10, weight="bold")
        d.ax.plot([x, x], [2, top], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    colors = {"status": P["accent"], "cmd": P["orange"], "cmd_opt": P["orange"],
              "op": P["violet"]}
    y = top - 4.5
    step = 4.9
    for x1, x2, label, kind, phase in STEPS:
        ls = "--" if kind == "cmd_opt" else "-"
        d.arrow(x1, y, x2, y, color=colors[kind], ls=ls)
        d.text((x1 + x2) / 2, y + 1.35, label, size=8.3, color=colors[kind])
        if phase:
            d.text(2, y, phase, size=8.5, color=P["dim"], ha="left", weight="bold")
        y -= step


diagram("13-p7-tractor-control-sequence", draw, w=12.5, h=8.2, xmax=100, ymax=67)

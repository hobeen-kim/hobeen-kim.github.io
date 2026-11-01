"""CH24 작업기의 후방 히치 원격 제어 메시지 순서(메시지 이름으로 표시) (light/dark PNG)."""
from _common import diagram

OP, TECU, IMP = 19, 51, 85

STEPS = [
    # (from, to, label, kind, phase)
    (TECU, IMP, "기능 확인 응답 (Tractor facility response)", "status", "기능 확인"),
    (IMP, TECU, "필요 기능 알림 (Required tractor facilities)", "cmd_opt", None),
    (TECU, IMP, "후방 히치 상태: 위치 40 %, limit 001", "status", "시작"),
    (IMP, TECU, "히치·PTO 명령: 후방 40 % (현재값 그대로)", "cmd", None),
    (TECU, IMP, "후방 히치 상태: limit 000 제한 없음", "status", None),
    (IMP, TECU, "히치·PTO 명령: 후방 64 % (100 ms마다)", "cmd", "원격 제어"),
    (OP, TECU, "캡에서 히치 수동 조작", "op", "운전자 개입"),
    (TECU, IMP, "후방 히치 상태: limit 001, exit 000011", "status", None),
    (IMP, TECU, "히치·PTO 명령: 현재 위치 (다시 맞춤)", "cmd", None),
    (TECU, IMP, "후방 히치 상태: limit 000 제한 없음", "status", None),
    (IMP, TECU, "히치·PTO 명령: FF (요청 없음)", "cmd", "반납"),
]


def draw(d):
    P = d.P
    top = 60
    lanes = [(OP, "운전자", P["gray"]), (TECU, "트랙터 (TECU)", P["blue"]),
             (IMP, "작업기 (작업기 ECU·TC)", P["green"])]
    for x, name, col in lanes:
        d.box(x - 11, top, 22, 5, col)
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
            d.text(1.5, y, phase, size=8.5, color=P["dim"], ha="left", weight="bold")
        y -= step


diagram("13-p7-tractor-control-sequence", draw, w=12.5, h=8.2, xmax=100, ymax=67)

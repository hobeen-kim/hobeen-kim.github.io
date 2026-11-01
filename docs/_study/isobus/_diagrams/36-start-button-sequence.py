"""36장 5절 예 1: 시작 버튼 → Button Activation → 살포 시작 → Change Numeric Value → 화면 갱신 시퀀스 (light/dark PNG)."""
from _common import diagram

LANE = {"user": 11, "vt": 48, "ecu": 86}
TOP = 97


def draw(d):
    P = d.P

    for key, name, col in (("user", "운전자", P["brown"]),
                           ("vt", "VT (디스플레이)", P["blue"]),
                           ("ecu", "작업기 ECU", P["green"])):
        x = LANE[key]
        d.box(x - 9, TOP - 5.5, 18, 5.5, col)
        d.text(x, TOP - 2.75, name, size=10.5, weight="bold")
        d.ax.plot([x, x], [1.5, TOP - 5.5], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def msg(src, dst, y, label, note=None, ls="-", color=None):
        x1, x2 = LANE[src], LANE[dst]
        c = color or (P["dim"] if ls == "--" else P["accent"])
        d.arrow(x1, y, x2, y, color=c, ls=ls)
        d.text((x1 + x2) / 2, y + 1.5, label, size=9.4, color=P["text"])
        if note:
            d.text((x1 + x2) / 2, y - 1.6, note, size=8.2, color=P["dim"])

    def act(lane, y, label, w=24):
        x = LANE[lane]
        d.box(x - w / 2, y - 2.1, w, 4.2, P["gray"], lw=1.1)
        d.text(x, y, label, size=9.0)

    msg("user", "vt", 87, '"시작" 버튼 터치', color=P["orange"])
    msg("vt", "ecu", 80, "Button Activation (PGN E600h)", "Object ID 0x0014 (20), 코드 1 (Pressed)")
    act("ecu", 73.5, "살포 시스템 시작")
    msg("ecu", "vt", 66.5, "Button Activation 응답 (PGN E700h)",
        "v5 이하 선택, v6 이상 200 ms 이내 필수", ls="--")
    msg("vt", "ecu", 59, "Button Activation (PGN E600h)", "코드 0 (Released)")
    msg("ecu", "vt", 52.5, "Button Activation 응답 (PGN E700h)", ls="--")
    act("ecu", 46.5, "살포량 센서 읽기 (예: 120 kg/h)", w=25)
    msg("ecu", "vt", 39.5, "Change Numeric Value (PGN E700h)", "Output Number 0x000B, 새 값 120")
    msg("vt", "user", 32.5, '"살포량: 120 kg/h" 표시', color=P["orange"])

    d.box(1.6, 2.5, 97.6, 23.5, "none", ec=P["violet"], lw=1.2)
    d.text(13, 24, "반복: 100 ms 주기 갱신 (예시)", size=8.8, color=P["violet"], ha="left")
    act("ecu", 19, "최신 센서값 읽기", w=20)
    msg("ecu", "vt", 12.5, "Change Numeric Value (새 살포량)")
    msg("vt", "user", 6.5, "화면 갱신", color=P["orange"])


diagram("36-start-button-sequence", draw, w=12, h=9.6, xmax=100, ymax=100)

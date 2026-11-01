"""36장 5절 예 2: 경고 발생 → Change Active Mask(Alarm Mask) → 운전자 확인 → Data Mask 복귀 시퀀스 (light/dark PNG)."""
from _common import diagram

LANE = {"ecu": 15, "vt": 52, "user": 87}
TOP = 73


def draw(d):
    P = d.P

    for key, name, col in (("ecu", "작업기 ECU", P["green"]),
                           ("vt", "VT", P["blue"]),
                           ("user", "운전자", P["brown"])):
        x = LANE[key]
        d.box(x - 9, TOP - 5.5, 18, 5.5, col)
        d.text(x, TOP - 2.75, name, size=10.5, weight="bold")
        d.ax.plot([x, x], [3, TOP - 5.5], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def msg(src, dst, y, label, note=None, color=None):
        x1, x2 = LANE[src], LANE[dst]
        c = color or P["accent"]
        d.arrow(x1, y, x2, y, color=c)
        d.text((x1 + x2) / 2, y + 1.5, label, size=9.4, color=P["text"])
        if note:
            d.text((x1 + x2) / 2, y - 1.7, note, size=8.2, color=P["dim"])

    def act(lane, y, label, w=27):
        x = LANE[lane]
        d.box(x - w / 2, y - 2.2, w, 4.4, P["gray"], lw=1.1)
        d.text(x, y, label, size=9.0)

    act("ecu", 61.5, "온도 임계값 초과 감지 (92°C > 90°C)")
    msg("ecu", "vt", 53.5, "Change Active Mask (PGN E700h)", "새 Active Mask: Alarm Mask 0x0003")
    msg("vt", "user", 45.5, '경고 화면 표시 ("온도 과열 경고!")',
        "Alarm Mask는 현재 Data Mask 위에 우선 표시", color=P["orange"])
    msg("user", "vt", 37.5, '소프트키 "확인" 누름', color=P["orange"])
    msg("vt", "ecu", 29.5, "Soft Key Activation (확인 키)")
    msg("ecu", "vt", 21.5, "Change Active Mask", "기존 Data Mask (ID 1)로 복귀")
    msg("vt", "user", 13.5, "일반 작업 화면 복원", color=P["orange"])


diagram("36-alarm-mask-sequence", draw, w=12, h=7.2, xmax=100, ymax=75)

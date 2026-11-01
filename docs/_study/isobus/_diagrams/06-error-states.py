"""CH6 4절 에러 상태 천이: Error Active, Error Passive, Bus Off와 전환 조건 (light/dark PNG)."""
from _common import diagram

BW, BH = 24, 15
Y = 22
XS = {"active": 8, "passive": 46, "busoff": 80}


def draw(d):
    P = d.P

    states = (
        ("active", "Error Active", "정상 동작", "TEC < 128 그리고 REC < 128", P["green"]),
        ("passive", "Error Passive", "제한 동작", "TEC ≥ 128 또는 REC ≥ 128", P["brown"]),
        ("busoff", "Bus Off", "버스에서 분리", "TEC > 255", P["purple"]),
    )
    for key, name, role, cond, fc in states:
        x = XS[key]
        w = BW if key != "busoff" else 18
        d.box(x, Y, w, BH, fc)
        d.text(x + w / 2, Y + BH * 0.74, name, size=11, weight="bold")
        d.text(x + w / 2, Y + BH * 0.47, role, size=9, color=P["dim"])
        d.text(x + w / 2, Y + BH * 0.2, cond, size=8.4)

    d.text(XS["active"] + BW / 2, Y + BH + 9.5, "시작(전원 투입)", size=8.6, color=P["dim"])
    d.arrow(XS["active"] + BW / 2, Y + BH + 7.6, XS["active"] + BW / 2, Y + BH + 0.6,
            color=P["edge"], lw=1.4)

    ax_r = XS["active"] + BW
    px = XS["passive"]
    d.arrow(ax_r + 0.6, Y + BH * 0.75, px - 0.6, Y + BH * 0.75, color=P["orange"])
    d.text((ax_r + px) / 2, Y + BH * 0.75 + 5.0, "TEC ≥ 128 또는", size=8.4, color=P["orange"])
    d.text((ax_r + px) / 2, Y + BH * 0.75 + 2.4, "REC ≥ 128", size=8.4, color=P["orange"])
    d.arrow(px - 0.6, Y + BH * 0.25, ax_r + 0.6, Y + BH * 0.25, color=P["accent"])
    d.text((ax_r + px) / 2, Y + BH * 0.25 - 2.4, "TEC < 128 그리고", size=8.4, color=P["accent"])
    d.text((ax_r + px) / 2, Y + BH * 0.25 - 5.0, "REC < 128", size=8.4, color=P["accent"])

    pr = XS["passive"] + BW
    bx = XS["busoff"]
    d.arrow(pr + 0.6, Y + BH / 2, bx - 0.6, Y + BH / 2, color=P["orange"])
    d.text((pr + bx) / 2, Y + BH / 2 + 2.4, "TEC > 255", size=8.4, color=P["orange"])

    d.arrow(bx + 9, Y - 0.6, XS["active"] + BW / 2, Y - 0.6, color=P["accent"], rad=-0.22)
    d.text(54, 11.0, "11개 연속 recessive 비트를 128번 감지 (자동 복구)", size=8.8,
           color=P["accent"])


diagram("06-error-states", draw, w=12, h=4.8, xmax=100, ymax=48)

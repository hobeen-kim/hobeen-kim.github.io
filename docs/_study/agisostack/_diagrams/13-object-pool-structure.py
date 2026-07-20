"""CH13 §2 오브젝트 풀 구조 — 워킹셋 아래 마스크와 하위 오브젝트 계층."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(36, 40, 28, 8, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 44, "WorkingSet (0)\nexample_WorkingSet", size=9.8, weight="bold")

    # 마스크 3종
    masks = [
        (2, "DataMask (1000)\nmainRunscreen_DataMask", P["blue"]),
        (35, "AlarmMask (2000)\nexample_AlarmMask", P["brown"]),
        (68, "SoftKeyMask (4000)\nmainRunscreen_SoftKeyMask", P["green"]),
    ]
    for x, label, fc in masks:
        d.box(x, 27, 30, 8, fc)
        d.text(x + 15, 31, label, size=9.2)
        d.arrow(50, 40, x + 15, 35, color=P["edge"], rad=0.0)

    # DataMask 자식
    for i, (label, fc) in enumerate([
        ("Container (3000)", P["chip"]),
        ("Button (6000/6001)\nPlus / Minus", P["chip"]),
        ("OutputNumber (12000)", P["chip"]),
    ]):
        y = 18 - i * 7.5
        d.box(2, y, 30, 6, fc, ec=P["edge"], lw=1.1)
        d.text(17, y + 3, label, size=8.6)
    d.arrow(17, 27, 17, 24, color=P["edge"], style="-", lw=1.1)
    d.arrow(17, 18, 17, 16.5, color=P["edge"], style="-", lw=1.1)
    d.arrow(17, 10.5, 17, 9, color=P["edge"], style="-", lw=1.1)

    # AlarmMask 자식
    d.box(35, 18, 30, 6, P["chip"], ec=P["edge"], lw=1.1)
    d.text(50, 21, "OutputString (11004)", size=8.6)
    d.arrow(50, 27, 50, 24, color=P["edge"], style="-", lw=1.1)

    # SoftKeyMask 자식
    d.box(68, 18, 30, 6, P["chip"], ec=P["edge"], lw=1.1)
    d.text(83, 21, "Key (5000/5001)\nalarm / acknowledgeAlarm", size=8.6)
    d.arrow(83, 27, 83, 24, color=P["edge"], style="-", lw=1.1)

    # 참조 전용 오브젝트
    d.box(50, 2, 48, 12, P["purple"], ec=P["edge"])
    d.text(74, 11.4, "참조 전용 오브젝트", size=9, color=P["dim"])
    d.text(74, 6.5, "NumberVariable (21000)  ·  StringVariable (22001)\n"
                    "FontAttributes (23002)  ·  LineAttributes (24000)\n"
                    "FillAttributes (25000)  ·  ObjectPointer (27000)", size=8.4)
    d.arrow(32, 5, 50, 8, color=P["violet"], ls="--", lw=1.3)
    d.text(40, 2.6, "value 참조", size=8.2, color=P["violet"])


diagram("13-object-pool-structure", draw, w=13, h=6.6, ymax=50)

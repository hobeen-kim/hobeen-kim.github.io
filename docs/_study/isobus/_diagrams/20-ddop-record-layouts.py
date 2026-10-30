"""CH20 §7 DDOP 오브젝트 레코드 5종(DVC·DET·DPD·DPT·DVP)의 필드 배치 (light/dark PNG)."""
from _common import diagram

HEAD, FIX, CNT, STR, V4 = "blue", "green", "gray", "brown", "purple"

# (박스 안 라벨, 박스 아래 크기, 색상 키, 폭)
RECORDS = [
    ("DVC", [
        ("Table ID\n'DVC'", "3", HEAD, 6.2),
        ("Object ID\n= 0", "2", HEAD, 6.0),
        ("N", "1", CNT, 3.0),
        ("designator", "N", STR, 7.4),
        ("M", "1", CNT, 3.0),
        ("SW\nversion", "M", STR, 6.2),
        ("ClientNAME", "8", FIX, 7.6),
        ("O", "1", CNT, 3.0),
        ("serial\nnumber", "O", STR, 6.2),
        ("structure\nlabel", "7", FIX, 7.4),
        ("localization\nlabel", "7", FIX, 8.6),
        ("P", "1", V4, 3.0),
        ("extended\nstructure label", "P (0~32)", V4, 10.2),
    ]),
    ("DET", [
        ("Table ID\n'DET'", "3", HEAD, 6.2),
        ("Object ID", "2", HEAD, 6.0),
        ("type\n1~7", "1", FIX, 5.0),
        ("N", "1", CNT, 3.0),
        ("designator", "N", STR, 7.4),
        ("element\nnumber", "2", FIX, 7.0),
        ("parent\nobject ID", "2", FIX, 7.4),
        ("개수 K", "2", CNT, 5.6),
        ("DPD·DPT\nobject ID 목록", "2 x K", FIX, 10.4),
    ]),
    ("DPD", [
        ("Table ID\n'DPD'", "3", HEAD, 6.2),
        ("Object ID", "2", HEAD, 6.0),
        ("DDI", "2", FIX, 5.0),
        ("properties\n비트", "1", FIX, 6.8),
        ("trigger\n비트", "1", FIX, 6.0),
        ("N", "1", CNT, 3.0),
        ("designator", "N", STR, 7.4),
        ("DVP\nobject ID", "2", FIX, 7.0),
    ]),
    ("DPT", [
        ("Table ID\n'DPT'", "3", HEAD, 6.2),
        ("Object ID", "2", HEAD, 6.0),
        ("DDI", "2", FIX, 5.0),
        ("value\nint32", "4", FIX, 6.8),
        ("N", "1", CNT, 3.0),
        ("designator", "N", STR, 7.4),
        ("DVP\nobject ID", "2", FIX, 7.0),
    ]),
    ("DVP", [
        ("Table ID\n'DVP'", "3", HEAD, 6.2),
        ("Object ID", "2", HEAD, 6.0),
        ("offset\nint32", "4", FIX, 6.8),
        ("scale\nfloat", "4", FIX, 6.8),
        ("decimals\n0~7", "1", FIX, 6.8),
        ("N", "1", CNT, 3.0),
        ("unit\ndesignator", "N", STR, 7.4),
    ]),
]

LEGEND = [
    (HEAD, "머리 (Table ID·Object ID)"),
    (FIX, "고정 길이 필드"),
    (CNT, "길이·개수 바이트"),
    (STR, "가변 길이 UTF-8"),
    (V4, "버전 4 전용"),
]

X0, GAP = 9.0, 0.32
BH = 4.6
ROW_TOP = 37.6
ROW_STEP = 8.6


def draw(d):
    P = d.P
    for r, (name, fields) in enumerate(RECORDS):
        y = ROW_TOP - r * ROW_STEP
        d.text(4.2, y + BH / 2, name, size=11, weight="bold", color=P["accent"])
        x = X0
        for label, size, color, w in fields:
            d.box(x, y, w, BH, P[color])
            d.text(x + w / 2, y + BH / 2, label, size=6.8)
            d.text(x + w / 2, y - 1.0, size, size=6.6, color=P["dim"])
            x += w + GAP

    ly = ROW_TOP + BH + 3.2
    for lx, (color, label) in zip((9, 31, 46, 61.5, 77), LEGEND):
        d.box(lx, ly - 0.8, 2.4, 1.6, P[color])
        d.text(lx + 3.0, ly, label, size=7.6, ha="left", color=P["dim"])


diagram("20-ddop-record-layouts", draw, w=13, h=6.2, xmax=100, ymax=47.2)

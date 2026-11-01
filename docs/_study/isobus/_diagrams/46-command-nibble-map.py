"""CH46 §2 명령 니블 0x0~0xF 지도: 읽는 법 네 무리와 예약, 먼저 익힐 명령 표시 (light/dark PNG)."""
from _common import diagram

BW, BH, GAP = 11, 12, 1
X0 = 2
ROW_Y = (25.5, 10.5)

GROUP_COLOR = {"sub": "purple", "common": "blue", "special": "brown", "status": "green", "rsv": "gray"}
CMDS = [
    ("0x0", "기술 정보\n(버전 등)", "sub"),
    ("0x1", "DDOP 관리", "sub"),
    ("0x2", "값 요청", "common"),
    ("0x3", "값 전달·설정", "common"),
    ("0x4", "측정:\n시간 간격", "common"),
    ("0x5", "측정:\n거리 간격", "common"),
    ("0x6", "측정:\n최소 임계값", "common"),
    ("0x7", "측정:\n최대 임계값", "common"),
    ("0x8", "측정:\n변화량", "common"),
    ("0x9", "Peer control\n할당", "special"),
    ("0xA", "설정 +\n확인 요구", "common"),
    ("0xB", "예약", "rsv"),
    ("0xC", "예약", "rsv"),
    ("0xD", "PDACK", "special"),
    ("0xE", "TC 상태", "status"),
    ("0xF", "클라이언트\n상태", "status"),
]
FIRST = {"0x2", "0x3", "0x4", "0x5", "0x6", "0x7", "0x8"}
LEGEND = [("sub", "하위 명령형"), ("common", "공통형"), ("special", "전용형"),
          ("status", "상태형"), ("rsv", "예약")]


def draw(d):
    P = d.P
    for i, (code, name, group) in enumerate(CMDS):
        x = X0 + (i % 8) * (BW + GAP)
        y = ROW_Y[i // 8]
        first = code in FIRST
        d.box(x, y, BW, BH, P[GROUP_COLOR[group]],
              ec=P["accent"] if first else None, lw=2.6 if first else 1.2)
        d.text(x + BW / 2, y + BH - 2.6, code, size=11.5)
        d.text(x + BW / 2, y + 4.0, name, size=8.2)

    x = X0
    for group, label in LEGEND:
        d.box(x, 2.2, 3.2, 3.2, P[GROUP_COLOR[group]], lw=1.0)
        d.text(x + 4.2, 3.8, label, size=9, ha="left")
        x += 15
    d.box(x + 2, 2.2, 3.2, 3.2, P["chip"], ec=P["accent"], lw=2.4)
    d.text(x + 6.2, 3.8, "먼저 익힐 명령(1절)", size=9, ha="left")


diagram("46-command-nibble-map", draw, w=12, h=4.6, xmax=100, ymax=38.5)

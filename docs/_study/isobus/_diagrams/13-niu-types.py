"""CH13 §6 NIU 유형별로 세그먼트 1의 프레임이 세그먼트 2에 어떻게 나타나는가 (light/dark PNG)."""
from _common import diagram

ROWS = [
    ("Repeater", "비트 단위 재생", "gray",
     "SA 0x80 · PGN X", "SA 0x80 · PGN X\n(그대로, 지연 < 0.1 bit)", "공유"),
    ("Bridge", "저장 후 전달 + 필터", "blue",
     "SA 0x80 · PGN X", "SA 0x80 · PGN X\n(필터 통과 시만)", "공유"),
    ("Router", "주소 변환", "green",
     "SA 0x80 · PGN X", "SA = 라우터 주소 · PGN X\n(address claim은 막힘)", "분리"),
    ("Gateway", "파라미터 재포장", "brown",
     "PGN X + PGN Y", "SA = 게이트웨이 · PGN Z\n(새로 묶은 메시지)", "분리"),
    ("Tractor ECU", "트랙터 대표 CF", "purple",
     "트랙터 버스 메시지", "SA = TECU · 표준 PGN\n(자기 SA로 재송신)", "분리"),
]


def draw(d):
    P = d.P
    top = 41
    row_h = 8.2
    box_h = 6.0

    d.text(17, top + 3.2, "세그먼트 1", size=10, weight="bold", color=P["dim"])
    d.text(46, top + 3.2, "NIU", size=10, weight="bold", color=P["dim"])
    d.text(76, top + 3.2, "세그먼트 2에 나타나는 모습", size=10, weight="bold", color=P["dim"])
    d.text(95, top + 3.2, "주소 공간", size=10, weight="bold", color=P["dim"])

    for i, (name, sub, color, src, dst, space) in enumerate(ROWS):
        y = top - i * row_h - box_h
        cy = y + box_h / 2

        d.box(5, y + 1.0, 24, box_h - 2.0, P["chip"])
        d.text(17, cy, src, size=9.5)

        d.arrow(29.5, cy, 35.5, cy)

        d.box(36, y, 20, box_h, P[color])
        d.text(46, cy + 1.2, name, size=10.5, weight="bold")
        d.text(46, cy - 1.4, sub, size=8.5, color=P["dim"])

        d.arrow(56.5, cy, 62.5, cy)

        d.box(63, y + 0.4, 26, box_h - 0.8, P["chip"])
        d.text(76, cy, dst, size=9)

        space_color = P["accent"] if space == "공유" else P["orange"]
        d.text(95, cy, space, size=10, weight="bold", color=space_color)


diagram("13-niu-types", draw, w=13, h=6.6, xmax=100, ymax=46)

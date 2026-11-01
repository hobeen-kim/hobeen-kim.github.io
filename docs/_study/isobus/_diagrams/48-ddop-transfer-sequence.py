"""48장 3절: TC 클라이언트가 DDOP를 TC에 올리고 활성화하는 순서 (light/dark PNG)."""
from matplotlib.patches import Rectangle

from _common import diagram

CX, TX = 16.0, 84.0
STEP = 5.4

# (방향 "ct" 클라이언트->TC | "tc" TC->클라이언트, 라벨)
BEFORE = [
    ("ct", "Working Set Master (PGN 65037): 버스 참여 알림"),
    ("ct", "Request Structure Label (01): 이 라벨의 DDOP가 있나?"),
    ("tc", "Structure Label (11): 있으면 같은 라벨, 없으면 FF x 7"),
]
ALT = [
    ("ct", "Request Object-pool Transfer (41): 보낼 크기"),
    ("tc", "Request Object-pool Transfer Response (51): 메모리 확인"),
    ("ct", "Object-pool Transfer (61): DDOP 레코드, TP/ETP로 분할"),
    ("tc", "Object-pool Transfer Response (71): 성공·실패"),
]
AFTER = [
    ("ct", "Object-pool Activate (81): 활성화 요청"),
    ("tc", "Object-pool Activate Response (91): 결과"),
]


def draw(d):
    P = d.P
    top = 77.0
    for x, name in ((CX, "TC 클라이언트\n(작업기 ECU)"), (TX, "TC")):
        d.box(x - 11, top, 22, 6.6, P["blue"], ec=P["accent"])
        d.text(x, top + 3.3, name, size=9, weight="bold")
        d.ax.plot([x, x], [top, 2.0], color=P["edge"], lw=1.1, ls="--", zorder=0.5)

    def note(y, s):
        d.box(CX - 6, y - 1.9, TX - CX + 12, 3.8, P["gray"], lw=0.9)
        d.text((CX + TX) / 2, y, s, size=7.8, color=P["dim"])

    def msg(y, way, label):
        x1, x2 = (CX, TX) if way == "ct" else (TX, CX)
        d.arrow(x1, y, x2, y, color=P["accent"] if way == "ct" else P["violet"],
                lw=1.5, ls="-" if way == "ct" else "--")
        d.text((CX + TX) / 2, y + 1.6, label, size=7.6)

    y = top - 4.6
    note(y, "주소 클레임 완료")
    y -= STEP
    for way, label in BEFORE:
        msg(y, way, label)
        y -= STEP

    # alt 프레임
    alt_top = y + 2.6
    d.text(CX - 9.5, alt_top - 1.6, "TC에 DDOP가 없거나\n버전이 다를 때", size=7.2,
           color=P["orange"], ha="left")
    y -= 2.4
    for way, label in ALT:
        msg(y, way, label)
        y -= STEP
    sep = y + 2.4
    d.arrow(CX - 10, sep, TX + 10, sep, color=P["orange"], lw=1.0, style="-", ls=":")
    y -= 1.8
    d.text(CX - 9.5, y + 0.6, "이미 있을 때", size=7.2, color=P["orange"], ha="left")
    d.box(TX - 24, y - 1.5, 30, 3.6, P["gray"], lw=0.9)
    d.text(TX - 9, y + 0.3, "저장된 DDOP를 그대로 쓴다", size=7.4, color=P["dim"])
    alt_bottom = y - 3.0
    d.ax.add_patch(Rectangle((CX - 10, alt_bottom), TX - CX + 20, alt_top - alt_bottom,
                             fill=False, edgecolor=P["orange"], linewidth=1.1,
                             linestyle="--", zorder=3))

    y = alt_bottom - 3.4
    for way, label in AFTER:
        msg(y, way, label)
        y -= STEP
    note(y + 0.6, "태스크 수행 준비 완료")


diagram("48-ddop-transfer-sequence", draw, w=11.5, h=8.4, xmax=100, ymax=85)

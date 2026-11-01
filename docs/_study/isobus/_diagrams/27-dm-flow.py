"""27장 1절 진단 메시지 흐름: 고장 발생부터 DM1·DM2·DM3까지 (light/dark PNG)."""
from _common import diagram

COLS = [(3, 22), (36, 26), (73, 24)]
ROWS = [31, 18, 5]


def node(d, col, row, label, fc, sub=None):
    x, w = COLS[col]
    y = ROWS[row]
    d.box(x, y, w, 8, fc)
    d.text(x + w / 2, y + 4, label, size=9.4)
    if sub:
        d.text(x + w / 2, y - 1.4, sub, size=8.4, color=d.P["dim"])


def link(d, row, c1, c2, color=None):
    x1 = COLS[c1][0] + COLS[c1][1]
    x2 = COLS[c2][0]
    y = ROWS[row] + 4
    d.arrow(x1 + 0.6, y, x2 - 0.6, y, color=color or d.P["accent"])


def draw(d):
    P = d.P
    node(d, 0, 0, "고장 발생\nSPN+FMI 감지", P["gray"])
    node(d, 1, 0, "DM1 전송\n활성 고장 코드, 1 Hz", P["blue"], "지금 켜진 경고등")
    node(d, 2, 0, "VT 화면에\n경고 표시", P["gray"])
    link(d, 0, 0, 1)
    link(d, 0, 1, 2)

    node(d, 0, 1, "고장 해소", P["gray"])
    node(d, 1, 1, "DM2로 이동\n이전 고장 기록", P["green"], "지난 고장 이력")
    link(d, 1, 0, 1)

    node(d, 0, 2, "정비사 요청", P["gray"])
    node(d, 1, 2, "DM3 전송\n고장 코드 초기화", P["brown"], "이력 지우기 명령")
    node(d, 2, 2, "DM2 기록 삭제", P["gray"])
    link(d, 2, 0, 1, color=P["orange"])
    link(d, 2, 1, 2, color=P["orange"])


diagram("27-dm-flow", draw, w=12, h=4.6, xmax=100, ymax=41)

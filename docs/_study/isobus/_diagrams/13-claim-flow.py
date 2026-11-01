"""CH13 주소 클레임 흐름도: 조회, 대기, 클레임, NAME 비교, 진 쪽의 처리 (light/dark PNG)."""
from _common import diagram


def node(d, cx, cy, w, h, text, fill, ec=None, lw=1.4, size=9):
    d.box(cx - w / 2, cy - h / 2, w, h, fill, ec=ec, lw=lw)
    d.text(cx, cy, text, size=size)


def draw(d):
    P = d.P
    mid, right, left = 60, 104, 16
    decision = dict(fill=P["chip"], ec=P["accent"], lw=1.8)

    node(d, mid, 78, 16, 5.5, "전원 ON", P["gray"])
    node(d, mid, 68, 40, 6, "Request for Address Claimed 송신", P["blue"])
    node(d, mid, 57.5, 40, 7.5, "250 ms + RTxD 대기\n(응답으로 사용 중인 주소 파악)", P["blue"])
    node(d, mid, 46.5, 40, 6, "빈 주소로 Address Claimed 송신", P["blue"])
    node(d, mid, 36, 40, 7.5, "같은 주소를 클레임하는\n다른 CF가 있나?", **decision)
    node(d, right, 36, 30, 7.5, "250 ms 동안 없으면\n일반 통신 시작", P["green"])
    node(d, mid, 24.5, 30, 7.5, "NAME 비교\n(작은 쪽이 이김)", **decision)
    node(d, right, 24.5, 30, 7.5, "Address Claimed 다시 송신\n(주소 지킴)", P["green"])
    node(d, mid, 12, 24, 6, "AAC 값은?", **decision)
    node(d, left, 12, 30, 7.5, "AAC=1: 128~247에서\n다른 주소로 다시 클레임", P["purple"])
    node(d, right, 12, 30, 7.5, "AAC=0: RTxD 뒤\nCannot Claim (SA 254)", P["brown"])

    for y1, y2 in ((75.25, 71.0), (65.0, 61.25), (53.75, 49.5), (43.5, 39.75)):
        d.arrow(mid, y1, mid, y2)

    d.arrow(80, 36, 89, 36)
    d.text(84.5, 38.3, "없음", size=8.5, color=P["accent"])
    d.arrow(mid, 32.25, mid, 28.25)
    d.text(62, 30.2, "있음", size=8.5, color=P["accent"], ha="left")
    d.arrow(75, 24.5, 89, 24.5)
    d.text(82, 26.8, "이김", size=8.5, color=P["accent"])
    d.arrow(mid, 20.75, mid, 15)
    d.text(62, 17.9, "짐", size=8.5, color=P["accent"], ha="left")
    d.arrow(48, 12, 31, 12)
    d.text(39.5, 14.2, "1", size=8.5, color=P["accent"])
    d.arrow(72, 12, 89, 12)
    d.text(80.5, 14.2, "0", size=8.5, color=P["accent"])
    d.arrow(right, 28.25, right, 32.25)

    d.ax.plot([left, left], [15.75, 46.5], color=P["violet"], lw=1.8, zorder=4)
    d.arrow(left, 46.5, 40, 46.5, color=P["violet"])


diagram("13-claim-flow", draw, w=11.5, h=7.9, xmax=120, ymax=82)

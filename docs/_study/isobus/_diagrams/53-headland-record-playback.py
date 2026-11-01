"""53장 도입: 헤드랜드 조작을 한 번 기록하고 다음부터 버튼 하나로 재생 (light/dark PNG)."""
from _common import diagram

STEPS = ["살포\n중지", "PTO\n끄기", "작업기\n들기", "회전", "작업기\n내리기", "PTO\n켜기", "살포\n재개"]
XS = [24, 35, 46, 57, 68, 79, 90]
CHIP_W, CHIP_H = 9, 8


def lane(d, cy, fc):
    P = d.P
    for x, s in zip(XS, STEPS):
        is_turn = s == "회전"
        d.box(x - CHIP_W / 2, cy - CHIP_H / 2, CHIP_W, CHIP_H, P["chip"] if is_turn else fc)
        d.text(x, cy, s, size=9.5, color=P["dim"] if is_turn else P["text"])


def draw(d):
    P = d.P

    # 같은 순서와 간격: 위아래 칸을 잇는 안내선
    for x in XS:
        d.ax.plot([x, x], [34, 20], color=P["edge"], lw=0.9, ls=(0, (3, 3)), zorder=1)

    # 기록 줄
    d.box(1, 33, 16, 10, P["green"])
    d.text(9, 38, "첫 헤드랜드\n운전자가 직접 조작\n(기록)", size=9)
    lane(d, 38, P["green"])

    # 재생 줄
    d.box(1, 11, 16, 10, P["blue"])
    d.text(9, 16, "다음 헤드랜드부터\n버튼 한 번\n(재생)", size=9)
    lane(d, 16, P["blue"])

    # 기록 → 재생
    d.arrow(9, 32.6, 9, 21.6, color=P["orange"])
    d.text(10.4, 27, "SCM이 순서와\n간격을 저장", size=8.5, color=P["orange"], ha="left")

    # 시간 축
    d.arrow(19.5, 5, 97, 5, color=P["dim"], lw=1.2)
    d.text(96.5, 7.4, "시간 또는 주행 거리", size=8.5, color=P["dim"], ha="right")


diagram("53-headland-record-playback", draw, w=12, h=5.0, xmax=100, ymax=48)

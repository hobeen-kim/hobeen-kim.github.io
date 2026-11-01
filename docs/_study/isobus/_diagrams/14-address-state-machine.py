"""CH14 주소 획득 상태 흐름: 미시도, 조회 대기, 클레임 중, 정상, 주소 없음 (light/dark PNG)."""
from _common import diagram

STATE_W, STATE_H = 20, 8


def state(d, cx, cy, name, fill):
    d.box(cx - STATE_W / 2, cy - STATE_H / 2, STATE_W, STATE_H, fill)
    d.text(cx, cy, name, size=10, weight="bold")


def draw(d):
    P = d.P
    not_tried, waiting, claiming, normal, no_address = (12, 30), (42, 30), (76, 30), (114, 30), (76, 7)

    state(d, *not_tried, "미시도", P["gray"])
    state(d, *waiting, "조회 대기", P["blue"])
    state(d, *claiming, "클레임 중", P["purple"])
    state(d, *normal, "정상", P["green"])
    state(d, *no_address, "주소 없음", P["brown"])

    d.arrow(22, 30, 32, 30)
    d.text(27, 37, "Request\n송신", size=8)
    d.arrow(52, 30, 66, 30)
    d.text(59, 37, "250 ms + RTxD 뒤\nAddress Claimed", size=8)
    d.arrow(86, 30, 104, 30)
    d.text(95, 33.4, "250 ms\n무경합", size=8)

    d.arrow(71, 34.1, 81, 34.1, color=P["violet"], rad=-1.2)
    d.text(76, 45.6, "졌을 때(self-configurable):\n다른 주소로 다시", size=8, color=P["violet"])

    d.arrow(110, 25.9, 82, 25.9, color=P["violet"], rad=-0.3)
    d.text(113, 19.0, "더 작은 NAME에 짐,\nCommanded Address 수락,\nNM Adopt", size=7.8,
           color=P["violet"])

    d.arrow(72, 25.9, 72, 11.1, color=P["orange"])
    d.text(70.5, 18.5, "졌을 때(non-configurable)\n또는 128~247이 다 참", size=8,
           color=P["orange"], ha="right")
    d.arrow(80, 11.1, 80, 25.9, color=P["accent"])
    d.text(81.5, 15.0, "Commanded Address\n수락", size=8, color=P["accent"], ha="left")

    d.ax.plot([66, 12], [7, 7], color=P["dim"], lw=1.8, zorder=4)
    d.arrow(12, 7, 12, 25.9, color=P["dim"])
    d.text(39, 9.2, "전원 재인가", size=8, color=P["dim"])


diagram("14-address-state-machine", draw, w=13, h=5.0, xmax=130, ymax=50)

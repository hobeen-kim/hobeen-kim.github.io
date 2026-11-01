"""25장: 반복 주기 변경 요청과 응답. 왼쪽은 송신자가 따를 때, 오른쪽은 따르지 못할 때."""
from _common import diagram


def lifeline(d, x, label, fc, top=52, bottom=6):
    P = d.P
    d.box(x - 9, top, 18, 6, fc)
    d.text(x, top + 3, label, size=10)
    d.ax.plot([x, x], [top, bottom], color=P["edge"], lw=1.2,
              ls=(0, (4, 3)), zorder=1)


def bracket(d, x, y1, y2, tick_dx, color):
    d.ax.plot([x + tick_dx, x, x, x + tick_dx], [y1, y1, y2, y2],
              color=color, lw=1.6, zorder=3)


def panel(d, req_x, snd_x, accept):
    P = d.P
    lifeline(d, req_x, "요청자\n(메시지를 쓰는 CF)", P["blue"])
    lifeline(d, snd_x, "송신자\n(그 PGN을 보내는 CF)", P["green"])

    d.arrow(req_x, 46, snd_x, 46)
    mid = (req_x + snd_x) / 2
    d.text(mid, 48.6, "Request for repetition rate", size=9.5)
    d.text(mid, 43.8, "PGN 52224, 목적지 지정", size=8.5, color=P["dim"])

    if accept:
        d.arrow(snd_x, 38, req_x, 38, color=P["violet"])
        d.text(mid, 40.6, "Response for repetition rate", size=9.5)
        d.text(mid, 35.8, "PGN 65038, 방송, 실제 주기", size=8.5, color=P["dim"])

        bracket(d, req_x - 1.5, 46, 38, -1.2, P["accent"])
        d.text(req_x - 4, 42, "250 ms\n안에 응답", size=8.5,
               color=P["accent"], ha="right")

        bracket(d, snd_x + 1.5, 38, 29, 1.2, P["orange"])
        d.text(snd_x + 4, 33.5, "250 ms\n기다림", size=8.5,
               color=P["orange"], ha="left")

        for y in (25, 19, 13):
            d.arrow(snd_x, y, req_x, y, color=P["dim"], lw=1.3, ls="--")
        d.text(mid, 27.3, "요청한 PGN을 새 주기로 송신", size=9, color=P["dim"])
    else:
        d.box(snd_x - 8, 34, 16, 6, P["gray"])
        d.text(snd_x, 37, "응답하지 않음", size=9)

        bracket(d, req_x - 1.5, 46, 30, -1.2, P["orange"])
        d.text(req_x - 4, 38, "250 ms\n응답 없음", size=8.5,
               color=P["orange"], ha="right")
        d.box(req_x - 8, 23.5, 16, 5, P["brown"])
        d.text(req_x, 26, "거절로 간주", size=9)

        for y in (17, 11):
            d.arrow(snd_x, y, req_x, y, color=P["dim"], lw=1.3, ls="--")
        d.text(mid, 19.3, "원래 주기 그대로 송신", size=9, color=P["dim"])


def draw(d):
    P = d.P
    d.text(29, 61.5, "송신자가 요청을 따를 때", size=10, color=P["dim"])
    d.text(78, 61.5, "송신자가 따를 수 없을 때", size=10, color=P["dim"])
    d.ax.plot([54, 54], [4, 63], color=P["edge"], lw=0.8, alpha=0.5)
    panel(d, 16, 42, accept=True)
    panel(d, 66, 92, accept=False)


diagram("25-repetition-rate-exchange", draw, w=13, h=7, xmax=104, ymax=64)

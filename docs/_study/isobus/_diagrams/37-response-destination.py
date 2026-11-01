"""37장 4절: member가 보낸 명령의 응답 목적지. 구성 1~3(Master로)과 구성 4(보낸 CF로) 비교 (light/dark PNG)."""
from _common import diagram


def panel(d, ox, title, direct):
    P = d.P
    d.box(ox, 1.5, 47, 45, P["chip"], ec=P["edge"], lw=1.0)
    d.text(ox + 23.5, 43.2, title, size=10, weight="bold", color=P["accent"])

    d.box(ox + 15.5, 30, 16, 7, P["blue"])
    d.text(ox + 23.5, 33.5, "VT", size=11, weight="bold")
    d.box(ox + 2, 5, 15, 7, P["green"])
    d.text(ox + 9.5, 8.5, "Master", size=10.5, weight="bold")
    d.box(ox + 30, 5, 15, 7, P["green"])
    d.text(ox + 37.5, 8.5, "member", size=10.5, weight="bold")

    d.arrow(ox + 35.5, 12.3, ox + 28.5, 29.7, color=P["accent"])
    if direct:
        d.text(ox + 29.6, 22.6, "① 명령", size=9, color=P["accent"], ha="right")
    else:
        d.text(ox + 34.4, 22.6, "① 명령", size=9, color=P["accent"], ha="left")

    if direct:
        d.arrow(ox + 31.2, 29.7, ox + 39.5, 12.3, color=P["dim"], ls="--")
        d.text(ox + 40.6, 21.2, "② 응답", size=9, color=P["dim"], ha="left")
        d.text(ox + 40.6, 18.6, "(보낸 CF로)", size=8.2, color=P["dim"], ha="left")
    else:
        d.arrow(ox + 18.5, 29.7, ox + 11, 12.3, color=P["dim"], ls="--")
        d.text(ox + 12.6, 23.4, "② 응답", size=9, color=P["dim"], ha="right")
        d.text(ox + 12.6, 20.8, "(Master로)", size=8.2, color=P["dim"], ha="right")
        d.arrow(ox + 15.2, 20.5, ox + 30.6, 10.2, color=P["violet"], ls=":", lw=1.6)
        d.text(ox + 27, 17.6, "③ 엿듣기", size=8.6, color=P["violet"])


def draw(d):
    panel(d, 1.5, "구성 1~3: 어느 한쪽이 v3 이하", direct=False)
    panel(d, 51.5, "구성 4: Working Set·VT 모두 v4 이상", direct=True)


diagram("37-response-destination", draw, w=12, h=5.8, xmax=100, ymax=48)

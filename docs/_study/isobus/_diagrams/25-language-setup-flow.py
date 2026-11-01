"""25장: 언어·형식·단위 설정이 운전자에서 VT, Working Set, TC, TC 클라이언트로 흐르는 길."""
from _common import diagram


def node(d, cx, cy, w, h, label, fc, size=10):
    d.box(cx - w / 2, cy - h / 2, w, h, fc)
    d.text(cx, cy, label, size=size)


def draw(d):
    P = d.P
    node(d, 9, 34, 14, 7, "운전자", P["gray"])
    node(d, 38, 34, 16, 9, "VT\n(설정의 출발점)", P["blue"])
    node(d, 38, 9, 16, 9, "TECU\n(기본 언어 보관)", P["green"])
    node(d, 82, 40, 26, 8, "Working Set\n(이 VT에 화면을 올린 작업기)", P["brown"], size=9.5)
    node(d, 66, 20, 14, 8, "TC", P["purple"])
    node(d, 91, 20, 16, 8, "TC 클라이언트", P["brown"], size=9.5)
    node(d, 91, 5.5, 16, 7, "Localization label\nBytes 1~6 + FF", P["chip"], size=8.5)

    d.arrow(16, 34, 30, 34)
    d.text(23, 36.2, "언어·단위 선택", size=8.5, color=P["dim"])

    d.arrow(35, 29.5, 35, 13.5, color=P["violet"])
    d.text(33.5, 21.5, "고른 적 없으면\n기본 언어 요청", size=8.5, color=P["violet"], ha="right")
    d.arrow(41, 13.5, 41, 29.5, color=P["violet"])
    d.text(42.5, 21.5, "기본 언어", size=8.5, color=P["violet"], ha="left")

    d.arrow(46, 36, 69, 40)
    d.text(57, 40.8, "Language command", size=8.5, color=P["dim"])
    d.arrow(46, 32, 59, 22.5)
    d.text(56.5, 29.5, "Language command", size=8.5, color=P["dim"], ha="left")
    d.arrow(73, 20, 83, 20, color=P["orange"])
    d.text(78, 23.2, "다시 알림", size=8.5, color=P["orange"])
    d.arrow(91, 16, 91, 9, color=P["edge"], lw=1.4)
    d.text(92.5, 12.5, "복사", size=8.5, color=P["dim"], ha="left")


diagram("25-language-setup-flow", draw, w=12.5, h=5, xmax=100, ymax=46)

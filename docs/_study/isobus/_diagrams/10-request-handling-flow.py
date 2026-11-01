"""CH10 §3~4 요청을 받은 장치의 판단 순서: 침묵, NACK, 응답 목적지와 TP (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(x, y, w, h, label, fc, ec=None, lw=1.4, size=9.0):
        d.box(x, y, w, h, fc, ec=ec, lw=lw)
        d.text(x + w / 2, y + h / 2, label, size=size)

    def lab(x, y, s, ha="center"):
        d.text(x, y, s, size=8.4, color=P["dim"], ha=ha)

    node(37, 63, 26, 6, "요청을 받음", P["chip"], ec=P["accent"], lw=1.8)
    node(35, 50, 30, 8, "요청된 PGN을\n보내는 장치인가?", P["purple"])

    node(2, 50, 26, 8, "전역 요청인가?\n(DA = 255)", P["purple"])
    node(1, 34, 13, 9, "침묵\nACK·NACK\n금지", P["gray"], size=8.6)
    node(16, 34, 13, 9, "NACK\n(control 1)", P["brown"], size=8.6)

    node(35, 35, 30, 8, "전역 요청인가?\n(DA = 255)", P["purple"])
    node(72, 35, 27, 8, "모두에게 응답\n8바이트 초과면 BAM", P["green"])
    node(35, 20, 30, 8, "PDU2이고\n8바이트 이하인가?", P["purple"])
    node(72, 20, 27, 8, "모두에게 응답\nPDU2에는 DA 칸이 없다", P["green"])
    node(35, 4, 30, 8, "요청자에게 응답\n8바이트 초과면 RTS/CTS", P["blue"])

    d.arrow(50, 63, 50, 58.4)
    d.arrow(35, 54, 28.4, 54, color=P["dim"])
    lab(31.7, 56, "아니오")
    d.arrow(8, 50, 7.5, 43.4, color=P["dim"])
    lab(6.5, 46.6, "예", ha="right")
    d.arrow(22, 50, 22.5, 43.4, color=P["dim"])
    lab(23.6, 46.6, "아니오", ha="left")

    d.arrow(50, 50, 50, 43.4)
    lab(51.5, 46.6, "예", ha="left")
    d.arrow(65, 39, 71.6, 39)
    lab(68.3, 41, "예")
    d.arrow(50, 35, 50, 28.4)
    lab(51.5, 31.6, "아니오", ha="left")
    d.arrow(65, 24, 71.6, 24)
    lab(68.3, 26, "예")
    d.arrow(50, 20, 50, 12.4)
    lab(51.5, 16.2, "아니오", ha="left")


diagram("10-request-handling-flow", draw, w=11, h=7.0, xmax=100, ymax=71)

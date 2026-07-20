"""CH11 §5 반복 주기 요청 — 스택은 요청만 전달하고, 주기 송신은 앱의 몫."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 24, 30, 12, P["blue"])
    d.text(17, 32, "요청자 CF", size=9.6)
    d.text(17, 27.5, "request_repetition_rate(\n  pgn, 100, src, dest)", size=8.2, color=P["dim"])

    d.text(45, 32.5, "PGN 52224 (0xCC00)", size=8.8, color=P["dim"])
    d.arrow(32, 30, 58, 30, color=P["accent"])

    d.box(58, 24, 38, 12, P["green"])
    d.text(77, 30, "수신 측 스택\n콜백 호출", size=9.2)

    d.arrow(77, 24, 77, 19, color=P["violet"])
    d.text(79.5, 21.5, "repetitionRate 저장", size=8.5, color=P["dim"], ha="left")

    d.box(58, 7, 38, 12, P["purple"])
    d.text(77, 13, "애플리케이션\n타이머 루프", size=9.2)

    d.arrow(58, 11, 17, 11, color=P["orange"], style="-")
    d.arrow(17, 11, 17, 24, color=P["orange"])
    d.text(37, 5.5, "요청한 PGN 을 앱이 직접 주기적으로 송신 (스택은 대신 보내주지 않는다)",
           size=8.8, color=P["dim"])


diagram("11-repetition-rate", draw, w=12.5, h=4.4, ymax=39)

"""35장 VT가 문자열 바이트를 8비트 문자열과 WideString으로 나눠 읽는 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    # 입력과 판별
    d.box(1, 19, 14, 7, P["gray"])
    d.text(8, 22.5, "문자열 바이트", size=9.5)
    d.arrow(15.3, 22.5, 19.7, 22.5)
    d.box(20, 18, 17, 9, P["brown"])
    d.text(28.5, 22.5, "첫 두 바이트가\nFF FE인가?", size=9.5)

    # 예: WideString
    d.box(45, 30, 20, 10, P["blue"])
    d.text(55, 35, "WideString\nUTF-16 리틀 엔디언\nFont type은 무시", size=9)
    d.arrow(37.3, 25, 44.7, 33, rad=-0.15)
    d.text(39.6, 30.5, "예", size=9, color=P["accent"])

    # 아니오: 8비트 문자열
    d.box(45, 5, 20, 10, P["green"])
    d.text(55, 10, "8비트 문자열\nFont type이\n문자 표를 고른다", size=9)
    d.arrow(37.3, 20, 44.7, 12, rad=0.15)
    d.text(39.4, 14.2, "아니오", size=9, color=P["accent"])

    # WideString: VT가 지원하는 글자인가
    d.box(73, 36, 25, 5, P["chip"], ec=P["accent"])
    d.text(85.5, 38.5, "그 글자를 표시", size=9)
    d.box(73, 28.5, 25, 5, P["chip"], ec=P["orange"])
    d.text(85.5, 31, "대체 문자로 표시", size=9)
    d.arrow(65.3, 36.5, 72.7, 38.5)
    d.text(69, 40.2, "지원하는 글자", size=8, color=P["dim"])
    d.arrow(65.3, 33.5, 72.7, 31, color=P["orange"])
    d.text(68.3, 28.2, "지원하지 않는 글자", size=8, color=P["dim"])

    # 8비트: Font type별 문자 표
    d.box(71, 1, 28, 21, P["chip"])
    lines = ["0  ISO 8859-1 (Latin 1)", "1  ISO 8859-15 (Latin 9)", "2  ISO 8859-2 (Latin 2)",
             "4  ISO 8859-4 (Latin 4)", "5  ISO 8859-5 (키릴)", "7  ISO 8859-7 (그리스)"]
    d.text(72.5, 20, "Font type  문자 표", size=8.5, color=P["dim"], ha="left")
    for i, s in enumerate(lines):
        d.text(72.5, 17.3 - i * 2.7, s, size=8.5, ha="left")
    d.arrow(65.3, 10, 70.7, 10)


diagram("35-string-decode-flow", draw, w=12, h=5.3, xmax=100, ymax=44)

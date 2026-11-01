"""51장 5절 응답 유실과 같은 TAN 재요청: FS가 실행 없이 기억한 응답을 다시 보내는 흐름 (light/dark PNG)."""
from _common import diagram

C, FS = 18, 66


def note(d, y, s, fc):
    d.box(69, y - 2.4, 30, 4.8, fc)
    d.text(84, y, s, size=8.4)


def draw(d):
    P = d.P
    for x, name in ((C, "클라이언트"), (FS, "File Server")):
        d.box(x - 10, 65, 20, 6, P["blue"] if x == FS else P["chip"])
        d.text(x, 68, name, size=10, weight="bold")
        d.arrow(x, 64.8, x, 12.5, color=P["edge"], lw=1.0, style="-", ls="--")

    d.arrow(C, 59, FS, 59, lw=1.5)
    d.text((C + FS) / 2, 60.7, "Read File, TAN 5, 4바이트", size=8.8)
    note(d, 55, "실행: ABCD 읽음, 포인터 이동", P["green"])

    d.arrow(FS, 51, 44, 51, lw=1.5, ls="--", color=P["orange"])
    d.text(55, 52.7, "응답 TAN 5: ABCD", size=8.8, color=P["orange"])
    d.text(41.5, 51, "X", size=15, weight="bold", color=P["orange"])
    d.text(35, 51, "버스에서 유실", size=8.4, color=P["orange"])

    d.arrow(C - 3, 51, C - 3, 43, color=P["violet"], lw=1.2, style="<|-|>")
    d.text(C - 4.5, 47, "busy 없이\n600 ms", size=8.2, color=P["violet"], ha="right")

    d.arrow(C, 41, FS, 41, lw=1.5)
    d.text((C + FS) / 2, 42.7, "Read File, TAN 5 (같은 TAN으로 다시)", size=8.8)
    note(d, 37, "직전 TAN과 같음: 실행하지 않음", P["brown"])

    d.arrow(FS, 33, C, 33, lw=1.5, ls="--")
    d.text((C + FS) / 2, 34.7, "기억해 둔 응답 재전송: TAN 5, ABCD", size=8.8)

    d.arrow(C, 24, FS, 24, lw=1.5)
    d.text((C + FS) / 2, 25.7, "Read File, TAN 6 (다음 요청)", size=8.8)
    note(d, 20, "새 TAN: 실행, EFGH 읽음", P["green"])

    d.arrow(FS, 16, C, 16, lw=1.5, ls="--")
    d.text((C + FS) / 2, 17.7, "응답 TAN 6: EFGH", size=8.8)

    d.box(C - 12, 5, 30, 5, P["chip"], ec=P["accent"])
    d.text(C + 3, 7.5, "받은 데이터: ABCD + EFGH", size=8.8, color=P["accent"])


diagram("51-fs-tan-retry", draw, w=12, h=7.0, xmax=100, ymax=72)

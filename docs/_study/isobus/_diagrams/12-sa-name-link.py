"""CH12 주소와 NAME의 관계: Address Claimed, 주소-NAME 대응표, 일반 프레임 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 6, 34, 32, P["blue"])
    d.text(19, 34.6, "① Address Claimed", size=10.5, weight="bold")
    d.text(19, 31.2, "(목적지: 모두)", size=8.5, color=P["dim"])
    d.box(5, 19, 28, 7, P["chip"], ec=P["accent"], lw=1.8)
    d.text(19, 22.5, "ID 끝 8비트: SA 0x80", size=9.5)
    d.box(5, 9.5, 28, 7, P["chip"])
    d.text(19, 13, "데이터 8바이트: NAME", size=9.5)

    d.box(44, 6, 36, 32, P["green"])
    d.text(62, 34.6, "② 주소-NAME 대응표", size=10.5, weight="bold")
    d.text(51.5, 30.2, "SA", size=8.5, color=P["dim"])
    d.text(68, 30.2, "NAME", size=8.5, color=P["dim"])
    rows = [("0x26", "VT의 NAME", 24.5), ("0x80", "0xA00882000D27A120", 17.0),
            ("0xF7", "TC의 NAME", 9.5)]
    for sa, name, y in rows:
        hot = sa == "0x80"
        ec = P["accent"] if hot else None
        lw = 1.8 if hot else 1.2
        weight = "bold" if hot else "normal"
        d.box(46.5, y - 3, 10, 6, P["chip"], ec=ec, lw=lw)
        d.text(51.5, y, sa, size=9.5, weight=weight)
        d.box(58, y - 3, 20, 6, P["chip"], ec=ec, lw=lw)
        d.text(68, y, name, size=8.3, weight=weight)

    d.box(88, 6, 30, 32, P["brown"])
    d.text(103, 34.6, "③ 일반 프레임", size=10.5, weight="bold")
    d.text(103, 31.2, "(측정값, 명령 등)", size=8.5, color=P["dim"])
    d.box(91, 19, 24, 7, P["chip"], ec=P["accent"], lw=1.8)
    d.text(103, 22.5, "ID 끝 8비트: SA 0x80", size=9.2)
    d.box(91, 9.5, 24, 7, P["chip"])
    d.text(103, 13, "데이터: 값", size=9.5)

    d.arrow(33.5, 22.5, 46.2, 17.6, color=P["accent"])
    d.text(39.8, 25.6, "짝을\n적어 둔다", size=8.3, color=P["accent"])
    d.arrow(90.7, 22.5, 78.4, 17.6, color=P["orange"])
    d.text(84.4, 25.6, "SA로\nNAME 찾기", size=8.3, color=P["orange"])


diagram("12-sa-name-link", draw, w=12, h=3.9, xmax=120, ymax=40)

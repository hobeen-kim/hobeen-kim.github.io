"""CH12 §11 ISO 11783 코드 요청·등록 흐름 — Part 1 Clause 7·Annex A (light/dark PNG)."""
from _common import diagram

LISTS = ["PGN\n할당", "Industry\ngroup", "IG 0\npreferred 주소", "IG 2\ninitial 주소",
         "NAME\n(function)", "All industry\nNAMEs", "Manufacturer\ncode"]


def draw(d):
    P = d.P
    y, h = 30, 11

    d.box(2, y, 20, h, P["chip"], ec=P["edge"])
    d.text(12, y + h / 2, "제조사·\n개발자", size=9.5, weight="bold")
    d.box(30, y, 24, h, P["blue"])
    d.text(42, y + h / 2, "isobus.net\n요청 양식", size=9)
    d.box(62, y, 26, h, P["brown"], ec=P["accent"], lw=1.6)
    d.text(75, y + h / 2, "유지관리 기관(MA)\nVDMA, DIN 대행", size=9)
    d.box(98, y, 30, h, P["purple"])
    d.text(113, y + h / 2, "SAE J1939 위원회", size=9)

    d.arrow(22, y + h / 2, 30, y + h / 2)
    d.text(26, y + h + 1.8, "신규·갱신\n요청", size=8, color=P["accent"])
    d.arrow(54, y + h / 2, 62, y + h / 2)
    d.arrow(88, y + h / 2, 98, y + h / 2, style="<|-|>")
    d.text(93, y + h + 1.8, "코드 등록\n동기화", size=8, color=P["accent"])
    d.text(75, y + h + 2.2, "ISO/TMB가 지정", size=8, color=P["dim"])

    # 전자 데이터베이스
    d.box(30, 3, 98, 19, P["gray"], ec=P["edge"])
    d.text(33, 19.2, "isobus.net 전자 데이터베이스 (SAE J1939에 공식 등록)", size=8.5,
           weight="bold", ha="left")
    cw, gap = 12.6, 1.2
    for i, name in enumerate(LISTS):
        x = 32 + i * (cw + gap)
        d.box(x, 5, cw, 10, P["green"])
        d.text(x + cw / 2, 10, name, size=7.6)

    d.arrow(75, y, 75, 22.3, color=P["accent"])
    d.text(77, 26, "게시", size=8, color=P["accent"], ha="left")
    d.arrow(30, 9, 12, 9, color=P["orange"], style="-")
    d.arrow(12, 9, 12, y, color=P["orange"])
    d.text(14, 18, "조회", size=8, color=P["orange"], ha="left")


diagram("12-code-request-flow", draw, w=13, h=5.0, xmax=130, ymax=48)

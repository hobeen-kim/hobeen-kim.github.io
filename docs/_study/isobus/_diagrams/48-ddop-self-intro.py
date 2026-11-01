"""48장 1절: 7섹션 붐 살포기의 자기소개서와 문장별 DDOP 오브젝트 (light/dark PNG)."""
from _common import diagram

TYPE_COLOR = {"DVC": "purple", "DET": "blue", "DPD": "green", "DPT": "brown", "DVP": "gray"}

CARD = [
    ("나는 붐 살포기다", "DVC", "장치 전체"),
    ("붐은 1개다", "DET", "Function"),
    ("섹션은 7개다", "DET", "Section x 7"),
    ("섹션 폭은 171.4 cm다", "DPT", "DDI 70"),
    ("살포량 목표를 받을 수 있다", "DPD", "DDI 1, settable"),
    ("실제 살포량을 알려 줄 수 있다", "DPD", "DDI 2"),
    ("값은 L/ha로 보여 준다", "DVP", "단위·배율"),
]


def draw(d):
    P = d.P
    # 주행 방향
    d.arrow(3.5, 26, 3.5, 40, color=P["dim"], lw=1.4)
    d.text(5.2, 38.5, "주행 방향", size=8, color=P["dim"], ha="left")

    # 트랙터, 탱크, 붐 (위에서 내려다본 모습)
    d.box(18, 36, 10, 8.5, P["gray"])
    d.text(23, 40.2, "트랙터", size=8.5)
    d.arrow(23, 36, 23, 32.2, color=P["edge"], lw=1.6, style="-")
    d.box(18.5, 26, 9, 6.2, P["gray"])
    d.text(23, 29.1, "탱크", size=8.5)
    d.arrow(23, 26, 23, 23.2, color=P["edge"], lw=1.6, style="-")

    x0, sw, by, bh = 3.0, 5.7, 19.0, 4.2
    for i in range(7):
        x = x0 + i * sw
        d.box(x + 0.15, by, sw - 0.3, bh, P["blue"], lw=1.1)
        d.text(x + sw / 2, by + bh / 2, str(i + 1), size=8.5, weight="bold")
    # 섹션 하나 폭
    d.arrow(x0 + 0.15, 16.6, x0 + sw - 0.15, 16.6, color=P["orange"], lw=1.2, style="<|-|>")
    d.text(x0 + sw / 2 + 2.2, 13.9, "섹션 하나 171.4 cm", size=7.6, color=P["orange"])
    # 붐 전체 폭
    d.arrow(x0 + 0.15, 9.6, x0 + 7 * sw - 0.15, 9.6, color=P["dim"], lw=1.2, style="<|-|>")
    d.text(x0 + 7 * sw / 2, 6.8, "붐 전체 11,998 mm (약 12 m)", size=7.6, color=P["dim"])

    # 살포기 -> 자기소개서
    d.arrow(44.5, 24, 49.5, 24, color=P["accent"], lw=2.0)

    # 자기소개서 카드
    cx, cy, cw, ch = 50.5, 2.5, 48.5, 42.5
    d.box(cx, cy, cw, ch, P["chip"], ec=P["accent"], lw=1.6)
    d.text(cx + 1.6, cy + ch - 2.6, "자기소개서 (DDOP)", size=9, weight="bold", ha="left")
    d.text(cx + cw - 1.6, cy + ch - 2.6, "담는 오브젝트", size=7.6, color=P["dim"], ha="right")
    row_h, top = 5.15, cy + ch - 6.4
    for i, (line, kind, note) in enumerate(CARD):
        y = top - i * row_h
        d.box(cx + 1.4, y - 2.0, 29.0, 4.0, P["bg"], lw=0.9)
        d.text(cx + 2.4, y, line, size=7.8, ha="left")
        d.box(cx + 31.4, y - 2.0, 6.2, 4.0, P[TYPE_COLOR[kind]], lw=0.9)
        d.text(cx + 34.5, y, kind, size=7.8, weight="bold")
        d.text(cx + 38.4, y, note, size=6.8, color=P["dim"], ha="left")


diagram("48-ddop-self-intro", draw, w=12.5, h=6.0, xmax=100, ymax=48)

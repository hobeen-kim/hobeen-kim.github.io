"""34장 색 해석 경로: 색 속성 → Colour Map → WS 팔레트(ARGB) → 알파 합성 → 픽셀 (light/dark PNG)."""
from _common import diagram

STAGES = [
    ("오브젝트 색 속성", "색 인덱스 0~255", "blue"),
    ("Colour Map", "색 번호 → 다른 색 번호", "green"),
    ("WS 팔레트 (ARGB)", "표준 팔레트 또는 Colour Palette", "purple"),
    ("알파 합성", "v6, 아래 색과 섞기", "brown"),
    ("화면 픽셀", "", "gray"),
]


def draw(d):
    P = d.P
    y, h, w, gap = 16, 9, 15.4, 4.4
    x = 2
    centers = []
    for title, sub, color in STAGES:
        d.box(x, y, w, h, P[color])
        if sub:
            d.text(x + w / 2, y + h / 2 + 1.4, title, size=9.5, weight="bold")
            d.text(x + w / 2, y + h / 2 - 1.6, sub, size=8, color=P["dim"])
        else:
            d.text(x + w / 2, y + h / 2, title, size=9.5, weight="bold")
        centers.append(x + w / 2)
        if x > 2:
            d.arrow(x - gap, y + h / 2, x, y + h / 2)
        x += w + gap

    # 초기 선택(로드 직후)과 런타임 전환
    top_y, bot_y = 33, 2
    for label, yy in [("Working Set Special Controls: 로드 직후 처음 쓸 표 선택", top_y),
                      ("Select Colour Map or Palette 명령: 운영 중 전환", bot_y)]:
        bx0, bx1 = centers[1] - w / 2, centers[2] + w / 2
        d.box(bx0, yy, bx1 - bx0, 6, P["chip"], ec=P["accent"])
        d.text((bx0 + bx1) / 2, yy + 3, label, size=8.5)
        for cx in centers[1:3]:
            if yy > y:
                d.arrow(cx, yy, cx, y + h, color=P["orange"], ls="--", lw=1.4)
            else:
                d.arrow(cx, yy + 6, cx, y, color=P["orange"], ls="--", lw=1.4)

    # 색 깊이 칩
    d.box(centers[0] - w / 2, top_y, w, 6, P["chip"], ec=P["edge"])
    d.text(centers[0], top_y + 3, "단색 0~1 / 16색 0~15\n256색 0~255", size=7.5, color=P["dim"])
    d.arrow(centers[0], top_y, centers[0], y + h, color=P["dim"], lw=1.2, style="-")


diagram("16-colour-pipeline", draw, w=13, h=4.6, xmax=100, ymax=41)

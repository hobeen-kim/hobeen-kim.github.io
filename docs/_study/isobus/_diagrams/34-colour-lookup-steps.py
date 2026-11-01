"""34장 색 번호가 실제 색이 되는 단계를 예 세 개로 따라가기 (light/dark PNG)."""
from _common import diagram

COLS = [
    # (머리글, x, 폭, 팔레트 키)
    ("1. 오브젝트의 색 번호", 9, 14, "blue"),
    ("2. Colour Map", 27, 16, "green"),
    ("3. 바뀐 번호", 47, 10, "gray"),
    ("4. WS 팔레트", 61, 19, "purple"),
    ("5. 화면 색", 84, 14, "brown"),
]

ROWS = [
    ("예 1", ["배경색 0", "없음(그대로)", "0", "표준 팔레트 0번\n000000", "검정"]),
    ("예 2", ["배경색 0", "0과 1을 맞바꿈", "1", "표준 팔레트 1번\nFFFFFF", "흰색"]),
    ("예 3 (v6)", ["배경색 2", "없음(그대로)", "2", "Colour Palette 2번\nA 80, RGB 009900",
                   "반투명 초록\n(아래 색과 섞임)"]),
]


def draw(d):
    P = d.P
    h = 7.5
    top = 40
    for title, x, w, _ in COLS:
        d.text(x + w / 2, top + 2.2, title, size=9.5, weight="bold")

    for r, (label, cells) in enumerate(ROWS):
        y = top - 3.5 - h - r * (h + 4.5)
        d.text(0.5, y + h / 2, label, size=9, color=P["dim"], ha="left")
        prev_right = None
        for (title, x, w, color), cell in zip(COLS, cells):
            d.box(x, y, w, h, P[color])
            d.text(x + w / 2, y + h / 2, cell, size=8.5)
            if prev_right is not None:
                d.arrow(prev_right + 0.4, y + h / 2, x - 0.4, y + h / 2)
            prev_right = x + w


diagram("34-colour-lookup-steps", draw, w=12, h=5.2, xmax=100, ymax=46)

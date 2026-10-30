"""CH20 §9 Device descriptor 하위 명령으로 본 DDOP 업로드 판단 흐름 (light/dark PNG)."""
from _common import diagram

W, H = 17.0, 6.0
COLS = [1.5, 21.0, 40.5, 60.0, 79.5]
LANES = [39.5, 24.5, 9.5]

# 키: (열, 레인, 라벨, 색상)
NODES = {
    "A": (0, 0, "Request Structure Label\n01 + 라벨 7B", "blue"),
    "B": (1, 0, "Structure Label\n11 + 라벨 | 7 x FF", "green"),
    "C": (2, 0, "Request Localization Label\n21 + 라벨 7B", "blue"),
    "D": (3, 0, "Localization Label\n31 + 라벨 | 7 x FF", "green"),
    "E": (1, 1, "Request Object-pool\nTransfer  41 + 크기 4B", "blue"),
    "F": (2, 1, "Request Object-pool\nTransfer Response  51", "green"),
    "G": (3, 1, "Object-pool Transfer\n61 + 레코드 (TP·ETP)", "blue"),
    "H": (4, 1, "Object-pool Transfer\nResponse  71", "green"),
    "I": (4, 2, "Object-pool Activate\n81 FF", "blue"),
    "J": (3, 2, "Activate Response\n91 + 오류 비트", "green"),
    "K": (2, 2, "활성 완료\nProcess Data 교환", "gray"),
    "L": (1, 2, "TC가 풀 삭제\n원인 수정 후 재전송", "brown"),
}


def box_of(key):
    c, l, _, _ = NODES[key]
    return COLS[c], LANES[l]


def right(key):
    x, y = box_of(key)
    return x + W, y + H / 2


def left(key):
    x, y = box_of(key)
    return x, y + H / 2


def top(key):
    x, y = box_of(key)
    return x + W / 2, y + H


def bottom(key):
    x, y = box_of(key)
    return x + W / 2, y


def draw(d):
    P = d.P
    for key, (_, _, label, color) in NODES.items():
        x, y = box_of(key)
        d.box(x, y, W, H, P[color])
        d.text(x + W / 2, y + H / 2, label, size=7.2)

    def lbl(x, y, s, ha="center"):
        d.text(x, y, s, size=7.4, color=P["dim"], ha=ha)

    d.arrow(*right("A"), *left("B"))
    d.arrow(*right("B"), *left("C"))
    lbl((right("B")[0] + left("C")[0]) / 2, right("B")[1] + 1.2, "일치")
    d.arrow(*right("C"), *left("D"))

    d.arrow(*bottom("B"), *top("E"), color=P["orange"])
    lbl(bottom("B")[0] + 1.0, (bottom("B")[1] + top("E")[1]) / 2, "7 x FF (없음)", ha="left")

    dx, dy = bottom("D")
    d.arrow(dx - 4, dy, top("E")[0] + 6, top("E")[1], color=P["orange"])
    lbl(58.5, 32.6, "불일치")

    d.arrow(*right("E"), *left("F"))
    d.arrow(*right("F"), *left("G"))
    lbl((right("F")[0] + left("G")[0]) / 2, right("F")[1] + 1.2, "0")
    lbl(bottom("F")[0], bottom("F")[1] - 1.3, "1 = 메모리 부족: 전송 안 함")
    d.arrow(*right("G"), *left("H"))

    d.arrow(*bottom("H"), *top("I"))
    lbl(bottom("H")[0] + 1.0, (bottom("H")[1] + top("I")[1]) / 2 + 0.6, "0", ha="left")
    lbl(bottom("H")[0] - 1.0, (bottom("H")[1] + top("I")[1]) / 2 + 0.6, "1·2 = 실패", ha="right")

    rx, ry = right("D")
    edge = 98.6
    d.arrow(rx, ry, edge, ry, style="-")
    d.arrow(edge, ry, edge, right("I")[1], style="-")
    d.arrow(edge, right("I")[1], *right("I"))
    lbl((rx + edge) / 2, ry + 1.2, "일치")

    d.arrow(*left("I"), *right("J"))
    d.arrow(*left("J"), *right("K"))
    lbl((left("J")[0] + right("K")[0]) / 2, left("J")[1] + 1.2, "0")
    jx, jy = bottom("J")
    kx, ky = bottom("L")
    d.arrow(jx, jy, kx, ky, color=P["orange"], rad=-0.28)
    lbl((jx + kx) / 2, 5.4, "byte 2 != 0")


diagram("20-ddop-upload-flow", draw, w=12, h=5.8, xmax=100, ymax=47.5)

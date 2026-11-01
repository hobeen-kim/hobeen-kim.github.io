"""15장 1절: 긴 데이터를 번호 붙은 CAN 프레임으로 나눠 보내고 다시 합치는 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    cy = 23

    stages = [(9.5, "큰 짐"), (29, "상자에 나눠 담기"), (53, "번호표 붙은 상자"),
              (77, "번호 순서대로 풀기"), (93.5, "원래 짐")]
    for x, label in stages:
        d.text(x, 47, label, size=9, color=P["dim"])

    d.box(2, cy - 6, 15, 12, P["brown"])
    d.text(9.5, cy, "큰 데이터\n(예: 200 byte)", size=10.5)
    d.arrow(17.6, cy, 22.2, cy)
    d.box(22.5, cy - 5, 13, 10, P["purple"])
    d.text(29, cy, "TP 분할\n(7 byte씩)", size=10.5)

    frames = [("1", "CAN Frame #1", "Seq=1, 7 byte", 37),
              ("2", "CAN Frame #2", "Seq=2, 7 byte", 29),
              ("3", "CAN Frame #3", "Seq=3, 7 byte", 21),
              ("N", "CAN Frame #N", "Seq=N, 나머지", 4)]
    fx, fw, fh = 42, 22, 6
    for seq, name, sub, y in frames:
        mid = y + fh / 2
        d.arrow(35.8, cy, fx - 0.4, mid, lw=1.3)
        d.box(fx, y, fw, fh, P["blue"])
        d.box(fx + 0.7, y + 0.9, 4.2, fh - 1.8, P["accent"], ec=P["accent"])
        d.text(fx + 2.8, mid, seq, size=10.5, color=P["bg"], weight="bold")
        d.text(fx + 13.6, mid, f"{name}\n{sub}", size=9)
        d.arrow(fx + fw + 0.4, mid, 70.2, cy, lw=1.3)
    d.ax.plot([fx + fw / 2] * 3, [16.2, 14, 11.8], "o", ms=2.6, color=P["dim"])

    d.box(70.5, cy - 5, 13, 10, P["purple"])
    d.text(77, cy, "수신 측\n재조립", size=10.5)
    d.arrow(83.8, cy, 87.7, cy)
    d.box(88, cy - 6, 11, 12, P["green"])
    d.text(93.5, cy, "원본 데이터\n복원", size=10.5)


diagram("15-tp-parcel-split", draw, w=13, h=5.2, xmax=100, ymax=50)

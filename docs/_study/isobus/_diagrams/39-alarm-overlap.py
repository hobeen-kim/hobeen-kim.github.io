"""39장: Working Set A·B의 경보가 겹칠 때 단계별 active mask와 VT 화면, 경보음이 나는 시점 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    X0, CW, GAP = 20, 14.6, 1.0
    cols = [X0 + i * (CW + GAP) for i in range(5)]

    heads = [("처음", "A가 active"),
             ("1단계", "B: Medium 경보"),
             ("2단계", "A: High 경보"),
             ("3단계", "A: Data Mask로"),
             ("4단계", "B: Data Mask로")]
    for x, (h1, h2) in zip(cols, heads):
        d.text(x + CW / 2, 50.5, h1, size=9.8, weight="bold")
        d.text(x + CW / 2, 47.6, h2, size=8.8, color=P["dim"])

    lanes = [(38.5, "Working Set A의\nactive mask"),
             (26.5, "Working Set B의\nactive mask"),
             (12.0, "VT 화면")]
    for y, label in lanes:
        d.text(1.5, y, label, size=9.2, weight="bold", ha="left")

    def cell(x, y, text, owner, alarm=False, h=7.0):
        fc = P["blue"] if owner == "A" else P["green"]
        ec = P["orange"] if alarm else P["edge"]
        d.box(x, y - h / 2, CW, h, fc, ec=ec, lw=2.2 if alarm else 1.1)
        d.text(x + CW / 2, y, text, size=8.8, weight="bold" if alarm else "normal")

    a_row = [("Data Mask", False), ("Data Mask", False), ("경보 High", True),
             ("Data Mask", False), ("Data Mask", False)]
    b_row = [("Data Mask", False), ("경보 Medium", True), ("경보 Medium", True),
             ("경보 Medium", True), ("Data Mask", False)]
    for x, (t, al) in zip(cols, a_row):
        cell(x, 38.5, t, "A", al)
    for x, (t, al) in zip(cols, b_row):
        cell(x, 26.5, t, "B", al)

    screen = [("A의 Data Mask", "A", False, ""),
              ("B의 경보", "B", True, "B 경보음"),
              ("A의 경보", "A", True, "A 경보음, B 소리 끊김"),
              ("B의 경보", "B", True, "B 경보음 다시"),
              ("A의 Data Mask", "A", False, "")]
    for x, (t, owner, al, sound) in zip(cols, screen):
        cell(x, 12.0, t, owner, al, h=8.0)
        if sound:
            d.text(x + CW / 2, 5.6, sound, size=8.4, color=P["orange"])

    for x in cols[:-1]:
        d.arrow(x + CW + 0.1, 12.0, x + CW + GAP - 0.1, 12.0, color=P["edge"], lw=1.2)

    d.ax.plot([X0 - 1, 98], [19.2, 19.2], color=P["edge"], ls=(0, (2, 3)), lw=1.0)


diagram("39-alarm-overlap", draw, w=13, h=6.6, xmax=100, ymax=54)

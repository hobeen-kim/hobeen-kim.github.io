"""39장: v6 활성화 메시지에서 TAN이 실리는 바이트와 그 바이트의 하위 니블 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    X0, CW, GAP, CH = 37, 7.2, 0.6, 5.6

    def cx(i):
        return X0 + i * (CW + GAP)

    for i in range(8):
        d.text(cx(i) + CW / 2, 52.5, f"Byte {i + 1}", size=8.8, color=P["dim"])

    rows = [
        ("Soft Key Activation (00)\nButton Activation (01)\nVT Select Input Object (03)\nVT ESC (04)",
         "00·01\n03·04", 8, "F"),
        ("VT Change Numeric Value (05)", "05", 4, "F"),
        ("Pointing Event (02)", "02", 6, "Touch\nState"),
        ("VT On User-Layout\nHide/Show (09)", "09", 8, "미정"),
        ("VT Control Audio Signal\nTermination (0A)", "0A", 3, "미정"),
    ]
    ys = [43.5, 34.0, 26.0, 18.0, 10.0]
    for (label, code, tan_byte, low), y in zip(rows, ys):
        h = 8.6 if "\n" in label and label.count("\n") >= 3 else CH
        d.text(1.5, y, label, size=8.8, ha="left", weight="bold")
        for i in range(8):
            x = cx(i)
            if i == 0:
                d.box(x, y - CH / 2, CW, CH, P["blue"], lw=1.1)
                d.text(x + CW / 2, y, code, size=8.8, weight="bold")
            elif i == tan_byte - 1:
                half = CW / 2
                d.box(x, y - CH / 2, half, CH, P["purple"], ec=P["accent"], lw=1.8)
                d.text(x + half / 2, y, "TAN", size=8.2, weight="bold", color=P["accent"])
                d.box(x + half, y - CH / 2, half, CH, P["chip"], ec=P["accent"], lw=1.8)
                d.text(x + half * 1.5, y, low, size=7.4)
            else:
                d.box(x, y - CH / 2, CW, CH, P["gray"], lw=0.9)

    d.text(X0, 3.2, "TAN 칸: 왼쪽 = 상위 니블(Bits 7~4), 오른쪽 = 하위 니블(Bits 3~0)",
           size=8.8, color=P["dim"], ha="left")


diagram("39-tan-position", draw, w=12.5, h=6.8, xmax=100, ymax=56)

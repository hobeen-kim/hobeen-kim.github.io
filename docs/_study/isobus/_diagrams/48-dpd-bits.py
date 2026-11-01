"""48장 5절: DPD 속성 바이트와 트리거 바이트의 비트 배치, Object 7·8 예 (light/dark PNG)."""
from _common import diagram

ROWS = [
    ("속성 바이트\n(properties)", "Object 7", "0x02",
     ["0", "0", "0", "0", "0", "control\nsource", "settable", "default\nset"],
     [0, 0, 0, 0, 0, 0, 1, 0]),
    ("트리거 바이트\n(trigger methods)", "Object 8", "0x08",
     ["0", "0", "0", "total", "on\nchange", "threshold\nlimits", "distance\ninterval", "time\ninterval"],
     [0, 0, 0, 0, 1, 0, 0, 0]),
]
X0, CW, GAP = 19.0, 8.0, 0.55


def draw(d):
    P = d.P
    for r, (title, obj, hexval, names, bits) in enumerate(ROWS):
        base = 27.0 - r * 22.0
        d.text(1.0, base + 7.0, title, size=8.4, weight="bold", ha="left")
        d.text(1.0, base + 2.4, obj, size=7.8, color=P["dim"], ha="left")
        for i, (name, bit) in enumerate(zip(names, bits)):
            x = X0 + i * (CW + GAP)
            unused = name == "0"
            d.box(x, base + 5.4, CW, 6.0, P["gray"] if unused else P["blue"], lw=1.0)
            d.text(x + CW / 2, base + 8.4, "안 씀" if unused else name, size=6.8,
                   color=P["dim"] if unused else None)
            on = bit == 1
            d.box(x, base, CW, 4.6, P["chip"], ec=P["accent"] if on else P["edge"],
                  lw=2.0 if on else 1.0)
            d.text(x + CW / 2, base + 2.3, str(bit), size=10, weight="bold",
                   color=P["accent"] if on else P["dim"])
            d.text(x + CW / 2, base - 1.6, f"bit {8 - i}", size=6.6, color=P["dim"])
        end = X0 + 8 * (CW + GAP)
        d.text(end + 0.8, base + 2.3, f"= {hexval}", size=10, weight="bold",
               color=P["accent"], ha="left")


diagram("48-dpd-bits", draw, w=12, h=5.4, xmax=100, ymax=45.5)

"""CH13 §10 Lighting command(PGN 65089) 8바이트 x 2비트 필드 배치 (light/dark PNG)."""
from _common import diagram

T, I, O, R = "blue", "green", "brown", "purple"

ROWS = [
    [("High-beam\nheadlights", O), ("Low-beam\nheadlights", O),
     ("Alternate\nheadlights", O), ("Daytime\nrunning lights", O)],
    [("Left-turn\nsignal", O), ("Right-turn\nsignal", O),
     ("Rotating\nbeacon", O), ("Tractor\nfront fog", T)],
    [("Left stop", O), ("Right stop", O),
     ("Centre stop", O), ("Back-up lights\n& alarm horn", O)],
    [("Tractor\nmarker", T), ("Implement\nmarker", I),
     ("Tractor\nclearance", T), ("Implement\nclearance", I)],
    [("Tractor rear\nhigh work", T), ("Tractor rear\nlow work", T),
     ("Tractor underside\nwork", T), ("Rear fog", O)],
    [("Tractor front\nhigh work", T), ("Tractor front\nlow work", T),
     ("Tractor side\nhigh work", T), ("Tractor side\nlow work", T)],
    [("Implement left\nforward work", I), ("Implement right\nforward work", I),
     ("Implement\nOEM option 1", I), ("Implement\nOEM option 2", I)],
    [("Implement\nrear work", I), ("Implement\nleft-facing work", I),
     ("Implement\nright-facing work", I), ("Lighting data\nrequest", R)],
]

LEGEND = [(T, "Tractor 램프"), (I, "Implement 램프"), (O, "공통·기타"),
          (R, "Lighting data 요청")]


def draw(d):
    P = d.P
    x0, cw, gap = 13, 21, 0.6
    top, rh, ch = 50, 5.3, 4.7

    for k, bits in enumerate(("Bits 8, 7", "Bits 6, 5", "Bits 4, 3", "Bits 2, 1")):
        d.text(x0 + k * (cw + gap) + cw / 2, top + 2.2, bits, size=9.5,
               weight="bold", color=P["dim"])

    for r, cells in enumerate(ROWS):
        y = top - (r + 1) * rh
        d.text(x0 - 6, y + ch / 2, f"Byte {r + 1}", size=9.5, weight="bold")
        for k, (label, color) in enumerate(cells):
            x = x0 + k * (cw + gap)
            d.box(x, y, cw, ch, P[color])
            d.text(x + cw / 2, y + ch / 2, label, size=8.5)

    lx = x0
    for color, label in LEGEND:
        d.box(lx, 1.2, 2.4, 1.8, P[color])
        d.text(lx + 3.2, 2.1, label, size=8.5, color=P["dim"], ha="left")
        lx += 21.6


diagram("13-light-command-layout", draw, w=13, h=8.2, xmax=100, ymax=54)

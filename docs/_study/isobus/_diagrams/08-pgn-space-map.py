"""CH08 §7 데이터 페이지 0·1의 PGN 공간과 할당 방향: Part 3 Table 2·Table 7 (light/dark PNG)."""
from _common import diagram

# (폭, 이름, 색, 왼쪽 PGN, 오른쪽 PGN): 폭은 보기 좋게 조정한 값(비례 아님)
SEG = [(40, "PDU1  (PS = DA)\nPF 0~238", "blue"),
       (7, "PF 239", "brown"),
       (40, "PDU2  (PS = GE)\nPF 240~254", "green"),
       (8, "PF 255", "brown")]
X0 = 4


def draw(d):
    P = d.P
    pages = [
        (31, "DP = 0", ["0", "60928 | 61184", "61440", "65279 | 65280", "65535"],
         ["Proprietary A", "Proprietary B"]),
        (7, "DP = 1", ["65536", "126464 | 126720", "126976", "130815 | 130816", "131071"],
         ["Proprietary A2", "표기 엇갈림"]),
    ]
    for y, name, edges, prop in pages:
        d.text(X0, y + 10.5, name, size=10, weight="bold", ha="left")
        x = X0
        xs = [x]
        for k, (w, label, c) in enumerate(SEG):
            ec = P["orange"] if (name == "DP = 1" and k == 3) else None
            d.box(x, y, w - 0.5, 6.5, P[c], ec=ec, lw=2.0 if ec else 1.4)
            d.text(x + (w - 0.5) / 2, y + 3.25, label, size=8.6)
            x += w
            xs.append(x - 0.5)
        d.text(X0 + 40 + 3.25, y - 1.6, prop[0], size=7.8, color=P["dim"])
        d.text(X0 + 87 + 3.75, y - 1.6, prop[1], size=7.8,
               color=P["orange"] if name == "DP = 1" else P["dim"])
        # PGN 경계값
        for xx, e in zip((xs[0], xs[1], xs[2], xs[3], xs[4]), edges):
            d.text(xx, y + 7.8, e, size=7.6, color=P["dim"])

        # 할당 방향 (Table 7): 100 ms 이하는 앞에서, 100 ms 초과는 뒤에서
        ay = y - 4.4
        for a0, a1, b1 in ((X0, X0 + 39.5, X0 + 39.5), (X0 + 47, X0 + 86.5, X0 + 86.5)):
            mid = (a0 + a1) / 2
            d.arrow(a0 + 0.5, ay, mid - 1.5, ay, color=P["accent"], lw=1.4)
            d.arrow(a1 - 0.5, ay, mid + 1.5, ay, color=P["violet"], lw=1.4)
            d.ax.plot([mid, mid], [ay - 1.2, ay + 1.2], color=P["edge"], lw=1.2)
        d.text(X0 + 10, ay - 1.9, "100 ms 이하, multi-packet 불가", size=7.8, color=P["accent"])
        d.text(X0 + 30, ay - 1.9, "100 ms 초과, 허용", size=7.8, color=P["violet"])
        d.text(X0 + 57, ay - 1.9, "100 ms 이하, multi-packet 불가", size=7.8, color=P["accent"])
        d.text(X0 + 77, ay - 1.9, "100 ms 초과, 허용", size=7.8, color=P["violet"])


diagram("08-pgn-space-map", draw, w=12.5, h=5.4, xmax=100, ymax=46)

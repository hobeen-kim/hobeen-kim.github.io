"""CH11 §4 16바이트 원본 데이터를 TP.DT 3패킷으로 분할하는 예시 (light/dark PNG)."""
from _common import diagram

GROUP_COLOR = {"A": "blue", "B": "green", "C": "purple"}
GROUPS = [("A", 7), ("B", 7), ("C", 2)]  # 원본 16바이트: A1~A7 | B1~B7 | C1~C2

PACKETS = [
    ("Packet #1", "01", [("A", i + 1) for i in range(7)]),
    ("Packet #2", "02", [("B", i + 1) for i in range(7)]),
    ("Packet #3", "03", [("C", 1), ("C", 2)]),
]

CW = 3.6
XMAX = 100


def draw(d):
    P = d.P

    # --- 위: 원본 16바이트 ---
    top_w = 16 * CW
    x0 = (XMAX - top_w) / 2
    top_y, h = 21, 5.5
    d.text(x0, top_y + h + 2.0, "원본 데이터 (16 byte)", size=9.5, ha="left", color=P["dim"])
    x = x0
    for name, n in GROUPS:
        color = GROUP_COLOR[name]
        for j in range(n):
            d.box(x, top_y, CW * 0.9, h, P[color])
            d.text(x + CW * 0.45, top_y + h / 2, f"{name}{j + 1}", size=8.5)
            x += CW

    # --- 아래: 3개 TP.DT 패킷 (Seq + 7 payload) ---
    n_cols = 8
    pgap = 2.6
    pw = n_cols * CW
    bottom_w = 3 * pw + 2 * pgap
    px0 = (XMAX - bottom_w) / 2
    py, ph = 5.5, 5.5

    x = px0
    for label, seq, cells in PACKETS:
        d.text(x, py + ph + 1.6, label, size=9, weight="bold", ha="left")
        d.box(x, py, CW * 0.9, ph, P["accent"])
        d.text(x + CW * 0.45, py + ph / 2, seq, size=8.5, color=P["bg"])
        cx = x + CW
        for gname, idx in cells:
            d.box(cx, py, CW * 0.9, ph, P[GROUP_COLOR[gname]])
            d.text(cx + CW * 0.45, py + ph / 2, f"{gname}{idx}", size=8.5)
            cx += CW
        for _ in range(n_cols - 1 - len(cells)):
            d.box(cx, py, CW * 0.9, ph, P["gray"])
            d.text(cx + CW * 0.45, py + ph / 2, "FF", size=8, color=P["dim"])
            cx += CW
        x += pw + pgap

    d.text(px0, py - 2.4, "Byte 1 = Seq, Byte 2~8 = 페이로드(마지막 패킷은 FF 패딩)",
           size=8.5, color=P["dim"], ha="left")


diagram("11-tpdt-segmentation", draw, w=13, h=4.6, xmax=XMAX, ymax=32)

"""CH3 2절 ID 0x100과 0x001의 중재: 비트 10부터 비교해 비트 8에서 0x100이 진다 (light/dark PNG)."""
from _common import diagram

A = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]   # 0x100, 비트 10..0
B = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]   # 0x001, 비트 10..0
LOSE = 2                                # 비트 8의 열 번호


def draw(d):
    P = d.P
    x0, cw, ch = 22, 6.2, 5.4
    rows = {"head": 33.5, "A": 26.5, "B": 19.5, "bus": 12.5}

    d.text(x0 - 2, rows["head"], "비트 위치", size=9.5, color=P["dim"], ha="right")
    d.text(x0 - 2, rows["A"], "노드 A\nID=0x100", size=10, ha="right")
    d.text(x0 - 2, rows["B"], "노드 B\nID=0x001", size=10, ha="right")
    d.text(x0 - 2, rows["bus"], "버스", size=10, weight="bold", ha="right")

    def cell(col, row, val, faded=False):
        x = x0 + col * cw
        y = rows[row] - ch / 2
        if faded:
            return
        fc = P["blue"] if val == 0 else P["chip"]
        d.box(x + 0.3, y, cw - 0.6, ch, fc)
        d.text(x + cw / 2, rows[row], str(val), size=11, weight="bold")

    for col in range(11):
        d.text(x0 + col * cw + cw / 2, rows["head"], str(10 - col), size=10, color=P["dim"])
        cell(col, "A", A[col], faded=col > LOSE)
        cell(col, "B", B[col])
        bus = B[col] if col > LOSE else (A[col] & B[col])
        cell(col, "bus", bus)

    # 비트 8 강조
    hx = x0 + LOSE * cw
    d.box(hx - 0.2, rows["bus"] - ch / 2 - 1, cw + 0.4, rows["A"] - rows["bus"] + ch + 2,
          "none", ec=P["orange"], lw=2.2)
    d.text(hx + cw / 2, 5, "비트 8: A는 1, B는 0 → 버스 0, A 패배", size=10, color=P["orange"], ha="left")

    # A가 물러난 구간
    fx = x0 + (LOSE + 1) * cw
    d.box(fx + 0.3, rows["A"] - ch / 2, (10 - LOSE) * cw - 0.6, ch, P["bg"], ec=P["edge"], lw=1.0)
    d.ax.patches[-1].set_linestyle("--")
    d.text(fx + (10 - LOSE) * cw / 2, rows["A"], "전송 중단: 버스가 빌 때까지 대기", size=10, color=P["dim"])
    d.text(x0 + 11 * cw + 1.2, rows["B"], "끝까지\n전송", size=9.5, color=P["accent"], ha="left")


diagram("03-arbitration-bits", draw, w=12, h=4.6, xmax=100, ymax=38)

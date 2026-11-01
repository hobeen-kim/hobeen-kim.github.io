"""37장 2절: 명령과 응답 프레임 비교. 반향 필드와 오류 코드 바이트 위치 (light/dark PNG)."""
from _common import diagram

ROLE = {"code": "blue", "id": "green", "val": "brown", "err": "purple", "rsv": "gray"}
X0, CW, GAP = 24, 8.6, 0.6


def cell_x(i):
    return X0 + i * (CW + GAP)


def draw(d):
    P = d.P

    def frame(y, label, sub, cells):
        d.text(X0 - 2, y + 3.2, label, size=10.5, weight="bold", ha="right")
        d.text(X0 - 2, y + 1.2, sub, size=8.4, color=P["dim"], ha="right")
        for i, (hexv, role, note) in enumerate(cells):
            x = cell_x(i)
            err = role == "err"
            d.box(x, y, CW, 5, P[ROLE[role]], ec=P["orange"] if err else None, lw=2.4 if err else 1.2)
            d.text(x + CW / 2, y + 3.25, hexv, size=11, weight="bold")
            d.text(x + CW / 2, y + 1.15, note, size=7.6, color=P["text"] if err else P["dim"])

    def under(i_from, i_to, y, label, color):
        xa, xb = cell_x(i_from), cell_x(i_to) + CW
        d.ax.plot([xa, xb], [y + 1.0, y + 1.0], color=color, lw=1.2)
        d.ax.plot([xa, xa], [y + 1.0, y + 1.7], color=color, lw=1.2)
        d.ax.plot([xb, xb], [y + 1.0, y + 1.7], color=color, lw=1.2)
        d.text((xa + xb) / 2, y - 0.4, label, size=8.4, color=color)

    for i in range(8):
        d.text(cell_x(i) + CW / 2, 59.2, f"Byte {i + 1}", size=8.2, color=P["dim"])

    d.text(2, 62.2, "Change Numeric Value (A8)", size=10.5, weight="bold", color=P["accent"], ha="left")
    frame(51.5, "명령", "PGN E700h", [
        ("A8", "code", "코드"), ("0B", "id", "ID"), ("00", "id", "ID"), ("FF", "rsv", "예약"),
        ("96", "val", "값"), ("00", "val", "값"), ("00", "val", "값"), ("00", "val", "값")])
    frame(43, "응답", "PGN E600h", [
        ("A8", "code", "코드"), ("0B", "id", "ID"), ("00", "id", "ID"), ("00", "err", "오류 코드"),
        ("96", "val", "값"), ("00", "val", "값"), ("00", "val", "값"), ("00", "val", "값")])
    under(1, 2, 39.6, "반향", P["dim"])
    under(3, 3, 39.6, "FF 자리에 오류 코드", P["orange"])
    under(4, 7, 39.6, "반향", P["dim"])

    d.text(2, 33.6, "Change String Value (B3)", size=10.5, weight="bold", color=P["accent"], ha="left")
    frame(23.5, "명령", "PGN E700h", [
        ("B3", "code", "코드"), ("14", "id", "ID"), ("00", "id", "ID"), ("02", "val", "길이"),
        ("00", "val", "길이"), ("4F", "val", "'O'"), ("4B", "val", "'K'"), ("FF", "rsv", "채움")])
    frame(13, "응답", "PGN E600h", [
        ("B3", "code", "코드"), ("FF", "rsv", "예약"), ("FF", "rsv", "예약"), ("14", "id", "ID"),
        ("00", "id", "ID"), ("04", "err", "오류 코드"), ("FF", "rsv", "예약"), ("FF", "rsv", "예약")])
    d.arrow((cell_x(1) + cell_x(2) + CW) / 2, 23.3, (cell_x(3) + cell_x(4) + CW) / 2, 18.2,
            color=P["violet"], lw=1.6, rad=0.18)
    under(3, 4, 9.6, "Object ID가 옮겨 옴", P["violet"])
    under(5, 5, 9.6, "04 = Bit 2", P["orange"])

    lx = 24
    for role, name in (("code", "VT function 코드"), ("id", "Object ID"), ("val", "값·길이·문자"),
                       ("err", "오류 코드"), ("rsv", "예약·채움")):
        err = role == "err"
        d.box(lx, 1.6, 2.4, 2.4, P[ROLE[role]], ec=P["orange"] if err else None, lw=1.8 if err else 1.0)
        d.text(lx + 3.2, 2.8, name, size=8.4, color=P["dim"], ha="left")
        lx += 15


diagram("37-response-anatomy", draw, w=12, h=7.6, xmax=100, ymax=64)

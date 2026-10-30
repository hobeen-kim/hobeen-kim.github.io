"""CH17 §8 매크로 참조(8/16비트)와 Macro 오브젝트 레코드 안 명령 패킷의 바이트 배치 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    BW, BH, GAP = 8.6, 6.0, 0.6
    X0 = 24

    def cell(x, y, w, val, sub, color):
        d.box(x, y, w, BH, P[color])
        d.text(x + w / 2, y + BH / 2 + 1.0, val, size=10, weight="bold")
        d.text(x + w / 2, y + BH / 2 - 1.3, sub, size=7.8)

    def row_label(y, s):
        d.text(2, y + BH / 2, s, size=9.5, weight="bold", ha="left")

    def bracket(x1, x2, y, label):
        d.ax.plot([x1, x2], [y, y], color=P["dim"], lw=1.2)
        d.ax.plot([x1, x1], [y, y + 0.7], color=P["dim"], lw=1.2)
        d.ax.plot([x2, x2], [y, y + 0.7], color=P["dim"], lw=1.2)
        d.text((x1 + x2) / 2, y - 1.5, label, size=8.5, color=P["dim"])

    # 행 1: 8비트 참조
    y1 = 44
    row_label(y1, "8비트 참조\n(2바이트)")
    cell(X0, y1, BW, "18", "Event ID 24", "purple")
    cell(X0 + (BW + GAP), y1, BW, "32", "Macro ID 50", "brown")

    # 행 2: 16비트 참조
    y2 = 28
    row_label(y2, "16비트 참조\n(4바이트, v5 이상)")
    xs = [X0 + i * (BW + GAP) for i in range(4)]
    cell(xs[0], y2, BW, "FF", "확장 참조 표시", "gray")
    cell(xs[1], y2, BW, "2C", "Macro ID 하위", "brown")
    cell(xs[2], y2, BW, "18", "Event ID 24", "purple")
    cell(xs[3], y2, BW, "01", "Macro ID 상위", "brown")
    d.arrow(xs[1] + BW / 2, y2 - 0.3, xs[3] + BW / 2 - 1.2, y2 - 0.3, color=P["orange"], rad=0.35, lw=1.4)
    d.text(xs[2] + BW / 2, y2 - 4.4, "Macro ID = 0x012C (300)", size=8.5, color=P["orange"])

    # 행 3: Macro 오브젝트 레코드
    y3 = 8
    row_label(y3, "Macro 오브젝트\n레코드")
    w_id, w_type, w_len = 10, 7, 10
    xa = X0
    cell(xa, y3, w_id, "32 00", "Object ID", "blue")
    xb = xa + w_id + GAP
    cell(xb, y3, w_type, "1C", "Type 28", "blue")
    xc = xb + w_type + GAP
    cell(xc, y3, w_len, "08 00", "뒤따를 바이트 수", "blue")
    xd = xc + w_len + GAP
    w_pkt = 44
    cell(xd, y3, w_pkt, "AD 00 00 02 00 FF FF FF", "명령 패킷 1개 = 8바이트 (짧으면 FF 채움)", "green")
    bracket(xd, xd + w_pkt, y3 - 1.2, "Annex F 명령 형식 그대로, Byte 1 = VT function")


diagram("17-macro-encoding", draw, w=13, h=6.6, xmax=100, ymax=54)

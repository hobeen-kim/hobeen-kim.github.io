"""CH10 Commanded Address 9바이트 구조와 8바이트 프레임 한계 (light/dark PNG)."""
from _common import diagram

N = 9
X0, BW, GAP = 7.0, 8.4, 1.5
BY, BH = 15.0, 10.0


def bx(i):
    return X0 + i * (BW + GAP)


def draw(d):
    P = d.P
    right8 = bx(7) + BW          # 8번 바이트 오른쪽 끝
    left9 = bx(8)                # 9번 바이트 왼쪽 끝
    divx = (right8 + left9) / 2

    # 바이트 칸
    for i in range(N):
        last = i == N - 1
        d.box(bx(i), BY, BW, BH,
              P["brown"] if last else P["blue"],
              ec=P["accent"] if last else P["edge"],
              lw=2.4 if last else 1.3)
        d.text(bx(i) + BW / 2, BY + BH / 2, f"Byte\n{i + 1}", size=9.5)

    # 상단 그룹 라벨
    d.ax.plot([bx(0), right8], [BY + BH + 2.2, BY + BH + 2.2],
              color=P["edge"], lw=1.2)
    for x in (bx(0), right8):
        d.ax.plot([x, x], [BY + BH + 1.2, BY + BH + 2.2], color=P["edge"], lw=1.2)
    d.text((bx(0) + right8) / 2, BY + BH + 4.4, "대상 NAME (64비트)", size=10.5)

    d.ax.plot([left9, left9 + BW], [BY + BH + 2.2, BY + BH + 2.2],
              color=P["accent"], lw=1.2)
    for x in (left9, left9 + BW):
        d.ax.plot([x, x], [BY + BH + 1.2, BY + BH + 2.2], color=P["accent"], lw=1.2)
    d.text(left9 + BW / 2, BY + BH + 4.4, "새 SA\n(8비트)", size=10, color=P["accent"])

    # 8바이트 경계
    d.ax.plot([divx, divx], [BY - 6.5, BY + BH + 7.5],
              color=P["orange"], lw=1.8, ls=(0, (5, 3)))
    d.text(divx - 1.5, BY - 4.6, "단일 CAN 프레임이 담을 수 있는 한계 →",
           size=9.5, color=P["orange"], ha="right")
    d.text(divx + 1.5, BY - 4.6, "← 1바이트 초과",
           size=9.5, color=P["orange"], ha="left")

    # 결론
    d.text(X0, BY - 10.5, "8바이트를 넘으므로 BAM으로 Global(255)에 전송한다",
           size=10.5, ha="left", color=P["text"])


diagram("10-commanded-address", draw, w=12, h=3.9, xmax=100, ymax=39)

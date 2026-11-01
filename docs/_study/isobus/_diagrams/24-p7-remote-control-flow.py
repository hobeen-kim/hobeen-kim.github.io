"""CH24 작업기의 트랙터 원격 제어 순서도: 기능 확인 → 현재값 맞추기 → 제어 → 개입 시 재일치 → 반납 (light/dark PNG)."""
from matplotlib.patches import Polygon

from _common import diagram

CX = 39
BW = 36


def step(d, y, title, sub, color):
    P = d.P
    d.box(CX - BW / 2, y - 4.2, BW, 8.4, P[color])
    d.text(CX, y + 1.5, title, size=11, weight="bold")
    d.text(CX, y - 1.8, sub, size=8.8, color=P["dim"])


def side(d, x0, y, title, sub):
    P = d.P
    d.box(x0, y - 4.2, 28, 8.4, P["gray"])
    d.text(x0 + 14, y + 1.5, title, size=10, weight="bold")
    d.text(x0 + 14, y - 1.8, sub, size=8.6, color=P["dim"])


def draw(d):
    P = d.P
    A = P["accent"]

    y1, y2, yd, y4, y5 = 65, 51, 37.5, 23.5, 8.5
    step(d, y1, "① 기능 확인", "이 트랙터가 해당 원격 명령을 지원하는가", "blue")
    step(d, y2, "② 현재값 맞추기", "상태 메시지의 현재값을 그대로 명령에 담는다", "blue")
    step(d, y4, "③ 원격 제어", "목표값을 100 ms마다 보내고 상태로 확인한다", "blue")
    step(d, y5, "④ 반납", "명령 필드를 전부 1(FF, 요청 없음)로 보낸다", "green")

    # decision diamond
    hw, hh = 15, 6
    d.ax.add_patch(Polygon([(CX, yd + hh), (CX + hw, yd), (CX, yd - hh), (CX - hw, yd)],
                           closed=True, facecolor=P["brown"], edgecolor=P["edge"],
                           linewidth=1.4, zorder=2))
    d.text(CX, yd + 1.4, "트랙터 응답이", size=9.2)
    d.text(CX, yd - 1.6, "limit 000(제한 없음)?", size=9.2, weight="bold")

    # main path
    d.arrow(CX, y1 - 4.2, CX, y2 + 4.3, color=A)
    d.text(CX + 1.2, (y1 + y2) / 2, "지원", size=8.8, color=A, ha="left")
    d.arrow(CX, y2 - 4.2, CX, yd + hh + 0.2, color=A)
    d.arrow(CX, yd - hh, CX, y4 + 4.3, color=A)
    d.text(CX + 1.2, (yd - hh + y4 + 4.2) / 2, "예", size=8.8, color=A, ha="left")
    d.arrow(CX, y4 - 4.2, CX, y5 + 4.3, color=A)
    d.text(CX + 1.2, (y4 + y5) / 2, "작업 끝", size=8.8, color=A, ha="left")

    # not supported
    side(d, 66, y1, "원격 제어하지 않는다", "운전자가 직접 조작")
    d.arrow(CX + BW / 2, y1, 66, y1, color=P["dim"])
    d.text((CX + BW / 2 + 66) / 2, y1 + 1.6, "미지원", size=8.8, color=P["dim"])

    # not accepted: re-match
    lx = 12
    d.ax.plot([CX - hw, lx], [yd, yd], color=P["violet"], lw=1.8, zorder=3)
    d.ax.plot([lx, lx], [yd, y2], color=P["violet"], lw=1.8, zorder=3)
    d.arrow(lx, y2, CX - BW / 2, y2, color=P["violet"])
    d.text((CX - hw + lx) / 2 + 0.5, yd + 1.6, "아니오", size=8.8, color=P["violet"])

    # operator intervention
    side(d, 66, y4, "기다리거나", "VT로 운전자에게 해제를 요청")
    d.arrow(CX + BW / 2, y4, 66, y4, color=P["violet"])
    d.text((CX + BW / 2 + 66) / 2, y4 + 3.4, "운전자 개입", size=8.8, color=P["violet"])
    d.text((CX + BW / 2 + 66) / 2, y4 + 1.4, "limit 001", size=8.8, color=P["violet"])
    rx = 80
    d.ax.plot([rx, rx], [y4 + 4.2, y2], color=P["violet"], lw=1.8, zorder=3)
    d.arrow(rx, y2, CX + BW / 2, y2, color=P["violet"])
    d.text(rx + 1.2, (y4 + y2) / 2 + 1.5, "다시 ②로", size=8.8, color=P["violet"], ha="left")
    d.text(rx + 1.2, (y4 + y2) / 2 - 1.0, "(재일치)", size=8.8, color=P["violet"], ha="left")


diagram("24-p7-remote-control-flow", draw, w=12, h=8.6, xmax=100, ymax=72)

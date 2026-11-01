"""53장 2절: 헤드랜드 관리의 기록·재생 흐름 (옛 mermaid 순서도를 옮김, light/dark PNG)."""
from matplotlib.patches import Polygon

from _common import diagram

LX, RX = 24.5, 75.5
NODE_W = 36


def node(d, cx, cy, h, label, fc):
    d.box(cx - NODE_W / 2, cy - h / 2, NODE_W, h, fc)
    d.text(cx, cy, label, size=9.5)


def decision(d, cx, cy, label, w=17, h=7):
    P = d.P
    d.ax.add_patch(Polygon([(cx - w / 2, cy), (cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2)],
                           closed=True, facecolor=P["purple"], edgecolor=P["edge"], lw=1.4, zorder=3))
    d.text(cx, cy, label, size=9.5)


def line(d, xs, ys):
    d.ax.plot(xs, ys, color=d.P["accent"], lw=1.8, zorder=4, solid_capstyle="round")


def draw(d):
    P = d.P

    # 두 묶음: 기록, 재생
    d.box(1, 1, 47, 68, P["gray"], ec=P["edge"], lw=1.0)
    d.text(3, 67.3, "기록", size=9.5, color=P["dim"], ha="left")
    d.box(52, 1, 47, 68, P["gray"], ec=P["edge"], lw=1.0)
    d.text(54, 67.3, "재생", size=9.5, color=P["dim"], ha="left")

    # 기록 열
    node(d, LX, 64, 5, "운전자: 기록 시작", P["chip"])
    node(d, LX, 55, 7, "SCM 상태 → Recording\nSCC들이 상태를 따라감", P["blue"])
    node(d, LX, 45, 7, "운전자가 평소처럼 조작\n살포 중지 / PTO 정지 / 작업기 상승", P["chip"])
    node(d, LX, 35, 7, "SCC: SCExecutionIndication 송신\n기능 ID + 상태 ID + 실행 상태", P["green"])
    node(d, LX, 25, 7, "SCM: trigger point와 함께\n스텝으로 저장", P["blue"])
    decision(d, LX, 15.5, "기록 정지?")
    node(d, LX, 6, 5, "시퀀스 저장 완료 → Ready", P["chip"])

    d.arrow(LX, 61.5, LX, 58.5)
    d.arrow(LX, 51.5, LX, 48.5)
    d.arrow(LX, 41.5, LX, 38.5)
    d.arrow(LX, 31.5, LX, 28.5)
    d.arrow(LX, 21.5, LX, 19)
    d.arrow(LX, 12, LX, 8.5)
    d.text(LX + 1.5, 10.3, "예", size=9, ha="left")

    # 기록 정지? 아니오 → 다시 조작
    line(d, [LX - 8.5, 4], [15.5, 15.5])
    line(d, [4, 4], [15.5, 45])
    d.arrow(4, 45, LX - NODE_W / 2, 45)
    d.text(10, 17.2, "아니오", size=9)

    # 재생 열 (가운데 맞춤)
    node(d, RX, 57.5, 7, "헤드랜드 도달\n운전자: 재생 시작", P["chip"])
    node(d, RX, 46.5, 7, "SCM: trigger point에 이르면\nSCMasterExecutionCommand 송신", P["blue"])
    node(d, RX, 35.5, 7, "SCC: 기능 실행 후\nSCClientExecutionStatus로\n시작·완료 보고", P["green"])
    decision(d, RX, 24.5, "시퀀스 끝?")
    node(d, RX, 13.5, 5, "Ready로 복귀", P["chip"])

    d.arrow(RX, 54, RX, 50)
    d.arrow(RX, 43, RX, 39)
    d.arrow(RX, 32, RX, 28)
    d.arrow(RX, 21, RX, 16)
    d.text(RX + 1.5, 18.6, "예", size=9, ha="left")

    # 시퀀스 끝? 아니오 → 다음 스텝 명령
    line(d, [RX + 8.5, 96.5], [24.5, 24.5])
    line(d, [96.5, 96.5], [24.5, 46.5])
    d.arrow(96.5, 46.5, RX + NODE_W / 2, 46.5)
    d.text(90, 26.2, "아니오", size=9)

    # 기록 끝 → 재생 시작
    line(d, [LX + NODE_W / 2, 50], [6, 6])
    line(d, [50, 50], [6, 57.5])
    d.arrow(50, 57.5, RX - NODE_W / 2, 57.5)


diagram("53-sc-flow", draw, w=12, h=8.4, xmax=100, ymax=70)

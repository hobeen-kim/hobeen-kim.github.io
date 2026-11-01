"""53장 1절: SCM(관리자)과 SCC(참여자)의 관계 (light/dark PNG)."""
from _common import diagram


def node(d, cx, cy, w, h, label, fc, size=10.5):
    d.box(cx - w / 2, cy - h / 2, w, h, fc)
    d.text(cx, cy, label, size=size)


def draw(d):
    P = d.P

    node(d, 50, 44, 30, 10, "SCM (관리자)\n기록과 재생을 이끈다", P["blue"])
    node(d, 24, 12, 30, 10, "SCC: 트랙터 ECU\n히치, PTO", P["green"])
    node(d, 76, 12, 30, 10, "SCC: 작업기 ECU\n밸브, 섹션", P["brown"])
    node(d, 10, 44, 14, 7, "운전자", P["chip"])

    # 운전자 → SCM, 운전자 → SCC
    d.arrow(17.2, 44, 34.6, 44, color=P["violet"])
    d.text(26, 46.4, "기록 시작\n재생 버튼", size=8.5, color=P["violet"], va="bottom")
    d.arrow(9, 40.2, 13.5, 17.4, color=P["violet"])
    d.text(4.5, 28, "평소처럼\n조작\n(기록할 때)", size=8.5, color=P["violet"])

    # SCM ↔ 트랙터 SCC
    d.arrow(38, 38.6, 25, 17.4, color=P["accent"])
    d.arrow(31, 17.4, 44, 38.6, color=P["orange"])
    # SCM ↔ 작업기 SCC
    d.arrow(62, 38.6, 75, 17.4, color=P["accent"])
    d.arrow(69, 17.4, 56, 38.6, color=P["orange"])

    d.text(25.5, 30, "실행 명령(재생)", size=8.5, color=P["accent"], ha="right")
    d.text(74.5, 30, "실행 명령(재생)", size=8.5, color=P["accent"], ha="left")
    d.text(50, 25.5, "조작 알림(기록)\n상태 보고(항상)", size=8.5, color=P["orange"])

    # SCC끼리는 직접 통신하지 않는다
    d.ax.plot([39.6, 60.4], [10, 10], color=P["edge"], lw=1.2, ls=(0, (4, 3)), zorder=2)
    d.text(50, 7.6, "직접 통신 없음", size=8.5, color=P["dim"])


diagram("53-sc-roles", draw, w=12, h=5.4, xmax=100, ymax=52)

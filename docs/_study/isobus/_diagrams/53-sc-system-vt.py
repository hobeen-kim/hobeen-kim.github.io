"""53장 4절: SC 시스템의 메시지 방향과 VT 연결 (옛 mermaid 그림을 옮김, light/dark PNG)."""
from _common import diagram


def node(d, cx, cy, w, h, label, fc):
    d.box(cx - w / 2, cy - h / 2, w, h, fc)
    d.text(cx, cy, label, size=10)


def draw(d):
    P = d.P

    d.box(2, 2, 66, 52, P["gray"], ec=P["accent"], lw=1.2)
    d.text(4, 51.6, "Sequence Control 시스템", size=9, color=P["dim"], ha="left")

    node(d, 35, 41, 26, 9, "SCM\n(기록·재생 관리)", P["blue"])
    node(d, 16, 15, 24, 9, "SCC: 트랙터 ECU\n(히치, PTO)", P["green"])
    node(d, 54, 15, 24, 9, "SCC: 작업기 ECU\n(밸브, 섹션)", P["brown"])
    node(d, 86, 28, 22, 11, "VT\n(function instance 0)", P["chip"])

    # 실행 명령: SCM → SCC (PGN 36352)
    d.arrow(29, 36.5, 14, 19.5, color=P["accent"])
    d.arrow(41, 36.5, 56, 19.5, color=P["accent"])
    d.text(18.5, 29.5, "실행 명령\nPGN 36352", size=8.5, color=P["accent"], ha="right")
    d.text(51.5, 29.5, "실행 명령\nPGN 36352", size=8.5, color=P["accent"], ha="left")

    # 조작 알림·상태: SCC → SCM (PGN 36096)
    d.arrow(20, 19.5, 33, 36.5, color=P["orange"])
    d.arrow(50, 19.5, 37, 36.5, color=P["orange"])
    d.text(35, 23.5, "조작 알림·상태\nPGN 36096", size=8.5, color=P["orange"])

    # SCM 화면 업로드
    d.arrow(48.4, 42, 76, 32.2, color=P["violet"], ls="--")
    d.text(86, 37, "SCM 화면(SCMOP) 업로드", size=8.5, color=P["violet"])

    # SCC 그림·글자 업로드: 두 SCC에서 아래로 모여 VT로
    dash = dict(color=P["violet"], lw=1.8, ls=(0, (5, 3)), zorder=4)
    d.ax.plot([16, 16], [10.5, 6], **dash)
    d.ax.plot([54, 54], [10.5, 6], **dash)
    d.ax.plot([16, 86], [6, 6], **dash)
    d.arrow(86, 6, 86, 22.3, color=P["violet"], ls="--")
    d.text(77, 8.2, "그림·글자(SCCOP) 업로드", size=8.5, color=P["violet"])


diagram("53-sc-system-vt", draw, w=12, h=6.7, xmax=100, ymax=56)

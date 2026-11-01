"""40장: 조이스틱(AUX 입력 유닛)의 입력을 작업기(기능 Working Set)의 기능에 연결하는 큰 그림과 주요 메시지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    B0, BH = 18, 29

    # AUX 입력 유닛
    d.box(2, B0, 26, BH, P["brown"], lw=1.4)
    d.text(15, 43.5, "AUX 입력 유닛", size=10.5, weight="bold")
    d.text(15, 40.6, "(조이스틱)", size=9, color=P["dim"])
    for y, t in [(33, "입력 0x0005"), (25, "입력 0x0006")]:
        d.box(5, y - 2.6, 20, 5.2, P["chip"], lw=1.0)
        d.text(15, y, t, size=9.2)

    # VT
    d.box(37, B0, 26, BH, P["blue"], lw=1.4)
    d.text(50, 43.5, "VT", size=10.5, weight="bold")
    d.text(50, 40.6, "(function instance 0)", size=9, color=P["dim"])
    d.box(40, 24.6, 20, 13, P["chip"], lw=1.0)
    d.text(50, 35.0, "할당 표", size=9.2, weight="bold")
    d.text(50, 31.2, "0x0005 → 0x0101", size=9)
    d.text(50, 27.8, "0x0006 → 0x0102", size=9)
    d.box(40, 19.4, 20, 4, P["purple"], lw=1.0)
    d.text(50, 21.4, "운전자 할당 화면", size=8.8)

    # 기능 Working Set
    d.box(72, B0, 26, BH, P["green"], lw=1.4)
    d.text(85, 43.5, "작업기", size=10.5, weight="bold")
    d.text(85, 40.6, "(기능 Working Set)", size=9, color=P["dim"])
    for y, t in [(33, "기능 0x0101"), (25, "기능 0x0102")]:
        d.box(75, y - 2.6, 20, 5.2, P["chip"], lw=1.0)
        d.text(85, y, t, size=9.2)

    # 메시지
    d.arrow(72, 51, 63, 51, color=P["accent"], lw=1.7)
    d.text(67.5, 52.9, "① 선호 할당 요청", size=8.8, color=P["accent"])
    d.arrow(37, 51, 28, 51, color=P["accent"], lw=1.7)
    d.text(32.5, 52.9, "② 상태 메시지 켜기", size=8.8, color=P["accent"])
    d.arrow(63, 14.5, 72, 14.5, color=P["accent"], lw=1.7)
    d.text(67.5, 12.3, "③ 할당 알림", size=8.8, color=P["accent"])

    d.ax.plot([15, 15, 85], [17.6, 7.5, 7.5], color=P["violet"], lw=1.8, zorder=4)
    d.arrow(85, 7.5, 85, 17.6, color=P["violet"], lw=1.8)
    d.text(50, 4.2, "④ 입력 값(Status): 버스 전체에 보내고, 할당받은 기능이 읽는다",
           size=8.8, color=P["violet"])


diagram("40-aux-big-picture", draw, w=12.5, h=6.8, xmax=100, ymax=56)

"""42장 태스크가 FMIS ↔ TC ↔ 작업기를 오가는 길과 표준이 정한 두 경계 (light/dark PNG)."""
from _common import diagram

Y, H = 14, 12


def node(d, x, w, title, sub, color, ec=None, lw=1.4):
    d.box(x, Y, w, H, d.P[color], ec=ec, lw=lw)
    d.text(x + w / 2, Y + H / 2 + 1.9, title, size=10.5, weight="bold")
    d.text(x + w / 2, Y + H / 2 - 1.9, sub, size=8.4)


def tag(d, x, y, label, std):
    P = d.P
    d.text(x, y, label, size=9, color=P["accent"] if std else P["dim"], weight="bold" if std else "normal")


def draw(d):
    P = d.P
    node(d, 1, 17, "FMIS", "계획·평가 소프트웨어", "gray")
    node(d, 22, 15, "XML 파일 세트", "TASKDATA.XML 등", "green", ec=P["accent"], lw=2.6)
    node(d, 41.5, 17.5, "드라이버·전달 수단", "USB 메모리, 무선 등", "gray")
    node(d, 63.5, 12, "TC", "Task Controller", "green")
    node(d, 84, 15, "작업기 ECU", "TC-Client", "blue")

    for x1, x2 in ((18.2, 21.8), (37.2, 41.3), (59.2, 63.3)):
        d.arrow(x1, Y + H / 2, x2, Y + H / 2, style="<|-|>", lw=1.6, color=P["edge"])
    d.arrow(75.7, Y + H / 2, 83.8, Y + H / 2, style="<|-|>", lw=2.6)
    d.text(79.75, Y + H / 2 + 2.4, "버스", size=8.4, color=P["accent"])
    d.text(79.75, Y + H / 2 - 2.4, "메시지", size=8.4, color=P["accent"])

    tag(d, 29.5, 29.2, "표준 ① 파일 형식", True)
    tag(d, 79.75, 29.2, "표준 ② 버스 통신", True)
    tag(d, 9.5, 11.2, "표준 밖", False)
    tag(d, 50.25, 11.2, "표준 밖", False)

    d.arrow(4, 36, 96, 36, color=P["orange"], lw=1.5)
    d.text(50, 38.3, "계획 태스크 (FMIS → TC → 작업기)", size=8.8, color=P["orange"])
    d.arrow(96, 4.6, 4, 4.6, color=P["violet"], lw=1.5)
    d.text(50, 2.2, "작업 결과 (작업기 → TC → FMIS)", size=8.8, color=P["violet"])


diagram("42-task-flow-boundary", draw, w=12, h=4.8, xmax=100, ymax=40)

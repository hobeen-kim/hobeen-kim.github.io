"""26장 2절 Working Set: 작업기 하나를 대표하는 팀(member)과 팀장(master) (light/dark PNG)."""
from _common import diagram


def node(d, x, y, w, h, title, body, fc):
    d.box(x, y, w, h, fc)
    d.text(x + w / 2, y + h - 2.6, title, size=9.8, weight="bold")
    d.text(x + w / 2, y + (h - 5.2) / 2 + 0.4, body, size=8.6)


def draw(d):
    P = d.P
    d.box(2, 2, 64, 55, P["chip"], ec=P["accent"], lw=1.6)
    d.text(4.5, 54, "Working Set: 파종기 (한 팀)", size=10, weight="bold",
           color=P["accent"], ha="left")

    node(d, 16, 34, 34, 12, "Working Set Master (팀장)",
         "파종기 메인 ECU, 주소 132\nVT·TC와 직접 통신, 작업기 대표", P["blue"])

    members = [
        (3, "Member 1 (팀원)", "섹션 밸브 ECU\n주소 133\n좌/우 섹션 개폐 제어"),
        (24, "Member 2 (팀원)", "속도 센서 ECU\n주소 134\n지면 속도 측정·보고"),
        (45, "Member 3 (팀원)", "비료 탱크 ECU\n주소 135\n잔량 센서, 경보"),
    ]
    for x, title, body in members:
        node(d, x, 6, 19, 14, title, body, P["green"])

    d.arrow(27, 34, 12.5, 20.4, color=P["accent"])
    d.text(13, 28.5, "내부 제어 명령", size=8.6, color=P["accent"], ha="left")
    d.arrow(33.5, 20.4, 33.5, 33.6, color=P["violet"])
    d.text(34.5, 26.5, "센서 값 수신", size=8.6, color=P["violet"], ha="left")
    d.arrow(54.5, 20.4, 41, 33.6, color=P["violet"])
    d.text(49.5, 28.5, "잔량 모니터링", size=8.6, color=P["violet"], ha="left")

    for y, title in ((40, "VT\n(트랙터 화면)"), (17, "TC\n(작업 컨트롤러)")):
        d.box(80, y, 18, 10, P["gray"])
        d.text(89, y + 5, title, size=9.6, weight="bold")
    d.arrow(80, 45, 50.4, 42.5, color=P["orange"])
    d.text(73, 47.2, "UI 데이터 요청", size=8.6, color=P["orange"])
    d.arrow(80, 22, 50.4, 36.5, color=P["orange"])
    d.text(73.5, 29.0, "섹션 명령", size=8.6, color=P["orange"])


diagram("26-working-set-team", draw, w=12, h=7, xmax=100, ymax=59)

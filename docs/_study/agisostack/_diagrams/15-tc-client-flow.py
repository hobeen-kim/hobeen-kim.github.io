"""CH15 TC 클라이언트 구성 순서와 런타임 콜백 루프."""
from _common import diagram


def draw(d):
    P = d.P

    # 준비 단계 (좌 → 우)
    steps = (
        (2, "TaskControllerClient\n(PartnerTC, InternalECU, VT)"),
        (27, "configure(myDDOP,\n붐 · 섹션 · 레이트 수, 지원 기능)"),
        (52, "콜백 2개 등록\nrequest / command"),
        (77, "initialize(true)"),
    )
    for x, label in steps:
        d.box(x, 30, 21, 10, P["blue"])
        d.text(x + 10.5, 35, label, size=8.8)
    for x in (23, 48, 73):
        d.arrow(x, 35, x + 4, 35, color=P["accent"])

    # 런타임 루프
    d.box(6, 6, 30, 15, P["green"])
    d.text(21, 18, "TC → 클라이언트", size=9.5, weight="bold")
    d.text(21, 12.5, "값 요청\nrequest_value_command_callback\n(elementNumber, DDI, &value)", size=8.4)

    d.box(64, 6, 30, 15, P["purple"])
    d.text(79, 18, "TC → 클라이언트", size=9.5, weight="bold")
    d.text(79, 12.5, "명령\ncommand_value_command_callback\n(elementNumber, DDI, value)", size=8.4)

    d.box(41, 9, 18, 9, P["chip"])
    d.text(50, 13.5, "애플리케이션\n상태", size=9, color=P["dim"])

    d.arrow(36, 13.5, 41, 13.5, color=P["orange"], style="<|-|>")
    d.arrow(64, 13.5, 59, 13.5, color=P["violet"], style="-|>")

    d.arrow(87.5, 30, 79, 21, color=P["edge"], lw=1.2)
    d.arrow(87.5, 30, 21, 21, color=P["edge"], lw=1.2, rad=-0.16)


diagram("15-tc-client-flow", draw, w=13, h=5.2, ymax=42)

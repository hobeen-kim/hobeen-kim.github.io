"""CH13 §3 이벤트 흐름 — 버튼 입력이 콜백을 거쳐 화면 갱신 명령으로 되돌아가는 경로."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽: VT 서버
    d.box(2, 12, 18, 16, P["brown"])
    d.text(11, 20, "VT 서버\n(터미널 화면)", size=10)

    # 가운데: 스택
    d.box(26, 8, 26, 24, P["blue"])
    d.text(39, 29, "VirtualTerminalClient", size=10, weight="bold")
    d.text(39, 23.5, "Button Activation\n메시지 파싱", size=8.8, color=P["dim"])
    d.box(28, 11, 22, 9, P["chip"], ec=P["edge"], lw=1.1)
    d.text(39, 15.5, "get_vt_button_\nevent_dispatcher()", size=8.4)

    # 오른쪽: 애플리케이션
    d.box(58, 20, 24, 12, P["green"])
    d.text(70, 26, "handle_button_event\n(VTKeyEvent)", size=9.2)

    d.box(58, 4, 24, 12, P["purple"])
    d.text(70, 10, "VirtualTerminalClient\nUpdateHelper", size=9.2)

    # 흐름
    d.arrow(20, 22, 26, 22, color=P["orange"])
    d.text(23, 23.6, "버튼 누름", size=8.2, color=P["orange"])
    d.arrow(50, 17, 58, 24, color=P["orange"])
    d.arrow(70, 20, 70, 16, color=P["accent"])
    d.text(72.5, 18, "increase_\nnumeric_value()", size=8, color=P["dim"], ha="left")

    d.arrow(58, 8, 39, 8, color=P["violet"], rad=-0.18)
    d.text(48, 3.4, "send_change_numeric_value()", size=8.2, color=P["violet"])
    d.arrow(26, 12, 20, 16, color=P["violet"])
    d.text(20, 10.4, "화면 갱신", size=8.2, color=P["violet"])

    # 이벤트 종류 목록
    d.box(86, 4, 12, 28, P["gray"], ec=P["edge"], lw=1.1)
    d.text(92, 30, "다른\n디스패처", size=8.6, color=P["dim"])
    d.text(92, 16, "SoftKey\nPointing\nSelectInput\nESC\nChangeNumeric\nChangeActiveMask\nChangeSoftKeyMask\nChangeString\nLayoutHideShow\nAudioTermination\nAuxiliaryFunction",
           size=7.6, color=P["dim"])
    d.arrow(82, 26, 86, 22, color=P["edge"], ls="--", lw=1.1)


diagram("13-vt-event-flow", draw, w=13, h=4.8, ymax=36)

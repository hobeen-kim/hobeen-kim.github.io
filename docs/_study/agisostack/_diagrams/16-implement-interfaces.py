"""CH16 §1 작업기 메시지 애플리케이션 계층 인터페이스 5종 (ISO 11783-7)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 27, 96, 9, P["blue"])
    d.text(50, 31.5, "애플리케이션  —  트랙터 ↔ 작업기 (ISO 11783-7)", size=10.5, weight="bold")

    cards = (
        (2, "HeartbeatInterface", "PGN 61668\n통신 무결성\n시퀀스 번호"),
        (21.6, "AgriculturalGuidance\nInterface", "조향 곡률 명령\n조향 시스템 상태\n100 ms 주기"),
        (41.2, "MaintainPower\nInterface", "키 OFF 후\n전원 2초 연장\n액추에이터 전원"),
        (60.8, "ShortcutButton\nInterface", "PGN 64770\n전 작업기 정지\n(ISB)"),
        (80.4, "SpeedMessages\nInterface", "휠 · 지면 · 선택 속도\n속도 지령"),
    )
    for x, title, body in cards:
        d.box(x, 2, 17.6, 20, P["green"])
        d.text(x + 8.8, 18, title, size=8.8, weight="bold")
        d.text(x + 8.8, 9, body, size=8.2, color=P["dim"])
        d.arrow(x + 8.8, 27, x + 8.8, 22, color=P["edge"], lw=1.2)


diagram("16-implement-interfaces", draw, w=13.5, h=4.4, ymax=38)

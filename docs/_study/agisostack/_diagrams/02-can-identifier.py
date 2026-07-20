"""CH02 CAN 프레임 — 32비트 식별자에 담긴 것과 8바이트 페이로드 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 식별자
    d.box(4, 26, 56, 20, P["blue"])
    d.text(32, 43.4, "32비트 식별자", size=11, weight="bold", color=P["accent"])
    fields = [
        ("우선순위", "충돌 시 승자 결정\n(하드웨어가 처리)"),
        ("PGN", "무엇에 대한 메시지인가\n= 메일 제목"),
        ("소스 주소", "누가 보냈나\n= 보내는 사람 주소"),
        ("목적지 주소", "누구에게 보내나\n(PGN이 결정)"),
    ]
    for i, (name, sub) in enumerate(fields):
        x = 6 + i * 13.5
        d.box(x, 28.5, 12, 11.5, P["chip"])
        d.text(x + 6, 37.2, name, size=9, weight="bold")
        d.text(x + 6, 32.4, sub, size=7.2, color=P["dim"])

    # 페이로드
    d.box(66, 26, 30, 20, P["green"])
    d.text(81, 43.4, "데이터 페이로드", size=11, weight="bold", color=P["accent"])
    for i in range(8):
        x = 68 + i * 3.4
        d.box(x, 31, 3.0, 7, P["chip"])
        d.text(x + 1.5, 34.5, str(i), size=8, color=P["dim"])
    d.text(81, 28.4, "최대 8바이트", size=9, color=P["dim"])

    # 버스
    d.box(4, 6, 92, 12, P["gray"])
    d.text(50, 14.6, "ISOBUS 네트워크 — 250 kbit/s CAN 버스", size=11, weight="bold")
    for i, label in enumerate(["트랙터 ECU", "Virtual Terminal", "살포기 ECU", "GPS 수신기"]):
        x = 8 + i * 22
        d.box(x, 8, 19, 4.6, P["chip"])
        d.text(x + 9.5, 10.3, label, size=8.5)

    d.arrow(32, 26, 32, 18, color=P["accent"], lw=1.6)
    d.arrow(81, 26, 81, 18, color=P["accent"], lw=1.6)


diagram("02-can-identifier", draw, w=11.5, h=5.6, ymax=48)

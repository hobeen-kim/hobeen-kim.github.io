"""CH01 계층 구조 — 애플리케이션 / AgIsoStack++ / 하드웨어 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 애플리케이션
    d.box(8, 40, 84, 9, P["green"])
    d.text(50, 46.4, "내 애플리케이션", size=12, weight="bold")
    d.text(50, 42.6, "살포량 계산 · 화면 로직 · 작업 기록", size=9, color=P["dim"])

    # 스택
    d.box(8, 13, 84, 23, P["blue"], ec=P["accent"], lw=2.0)
    d.text(50, 33.2, "AgIsoStack++", size=12, weight="bold", color=P["accent"])
    chips = [
        ("주소 클레임", "NAME → 주소 자동 확보"),
        ("전송 프로토콜", "TP · ETP · Fast Packet 자동 선택"),
        ("VT 클라이언트", "오브젝트 풀 업로드·이벤트"),
        ("TC 클라이언트", "DDOP · 프로세스 데이터"),
    ]
    for i, (name, sub) in enumerate(chips):
        x = 11 + i * 20.5
        d.box(x, 16, 18, 13, P["chip"])
        d.text(x + 9, 25.2, name, size=9.5, weight="bold")
        d.text(x + 9, 20.2, sub, size=7.8, color=P["dim"])

    # 하드웨어
    d.box(8, 1, 84, 8, P["gray"])
    d.text(50, 6.6, "HardwareInterface → CAN 드라이버", size=11, weight="bold")
    d.text(50, 3.0, "SocketCAN · TWAI(ESP32) · PEAK · InnoMaker · 가상 CAN",
           size=8.5, color=P["dim"])

    d.arrow(50, 40, 50, 36.2, color=P["accent"], style="<|-|>")
    d.arrow(50, 13, 50, 9.2, color=P["accent"], style="<|-|>")


diagram("01-stack-responsibility", draw, w=11, h=5.6, ymax=51)

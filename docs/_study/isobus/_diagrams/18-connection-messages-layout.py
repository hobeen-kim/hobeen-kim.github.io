"""CH18 §10 Version · TC Status · Client Task 메시지(8 byte) 바이트 배치 (light/dark PNG)."""
from _common import diagram

ROWS = [
    ("Version", "우선순위 5 · 상대 지정", [
        ("0x10", "Version", "blue"),
        ("버전", "0~4", "green"),
        ("부팅 시간", "s, TC/DL만", "green"),
        ("옵션 1", "bit 1~5", "brown"),
        ("옵션 2", "예약 0", "gray"),
        ("붐 수", "섹션 제어", "green"),
        ("섹션 수", "전체 붐 합", "green"),
        ("채널 수", "위치 기반 제어", "green"),
    ]),
    ("TC Status", "우선순위 3 · 전체에게", [
        ("0xFE", "TC Status", "blue"),
        ("0xFF", "element N/A", "gray"),
        ("0xFF", "DDI N/A", "gray"),
        ("0xFF", "DDI N/A", "gray"),
        ("상태 비트", "bit 1~4, 8", "brown"),
        ("클라이언트 SA", "Busy일 때만", "green"),
        ("처리 중 명령", "Busy일 때만", "green"),
        ("예약", "", "gray"),
    ]),
    ("Client Task", "우선순위 3 · 상대 지정", [
        ("0xFF", "Client Task", "blue"),
        ("0xFF", "element N/A", "gray"),
        ("0xFF", "DDI N/A", "gray"),
        ("0xFF", "DDI N/A", "gray"),
        ("상태", "bit 1 반향", "brown"),
        ("0x00", "예약", "gray"),
        ("0x00", "예약", "gray"),
        ("0x00", "예약", "gray"),
    ]),
]


def draw(d):
    P = d.P
    x0, w, gap, h = 8.2, 3.7, 0.25, 4.4
    for i in range(8):
        d.text(x0 + i * (w + gap) + w / 2, 23.9, f"Byte {i + 1}", size=9, weight="bold")
    for r, (name, sub, cells) in enumerate(ROWS):
        y = 17.6 - r * 7.0
        d.text(4.0, y + h / 2 + 0.8, name, size=10.5, weight="bold")
        d.text(4.0, y + h / 2 - 1.0, sub, size=7.6, color=P["dim"])
        for i, (val, note, color) in enumerate(cells):
            x = x0 + i * (w + gap)
            d.box(x, y, w, h, P[color])
            if note:
                d.text(x + w / 2, y + h / 2 + 0.85, val, size=9.2, weight="bold")
                d.text(x + w / 2, y + h / 2 - 1.0, note, size=7.3)
            else:
                d.text(x + w / 2, y + h / 2, val, size=9.2, weight="bold")


diagram("18-connection-messages-layout", draw, w=12, h=7, xmax=40, ymax=25.6)

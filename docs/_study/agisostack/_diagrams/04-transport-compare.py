"""CH04 전송 프로토콜 4종 — 크기 범위와 제약 비교 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    rows = [
        ("단일 CAN 프레임", "~ 8 바이트", "브로드캐스트·목적지 모두 가능", P["gray"], 78),
        ("TP (BAM)", "9 ~ 1785 바이트", "브로드캐스트 전용 · 프레임 간 필수 지연 · 동시 1건",
         P["brown"], 60),
        ("TP (Connection Mode)", "9 ~ 1785 바이트",
         "목적지 지정 전용 · 지연 없음 · RTS/CTS/EOMA 오버헤드", P["blue"], 42),
        ("ETP", "1786 ~ 117,440,505 바이트",
         "목적지 지정 전용 · 브로드캐스트 불가 · 수 분 소요 가능", P["green"], 24),
        ("NMEA 2000 Fast Packet", "~ 223 바이트",
         "프레임마다 PGN·우선순위 유지 · 일부 GNSS 메시지에 채택", P["purple"], 6),
    ]

    for name, size, note, fc, y in rows:
        d.box(3, y, 26, 14, fc)
        d.text(16, y + 7, name, size=10, weight="bold")
        d.box(31, y, 22, 14, P["chip"])
        d.text(42, y + 7, size, size=9.5, weight="bold", color=P["accent"])
        d.box(55, y, 42, 14, P["chip"])
        d.text(76, y + 7, note, size=8.4, color=P["dim"])


diagram("04-transport-compare", draw, w=12, h=5.6, ymax=94)

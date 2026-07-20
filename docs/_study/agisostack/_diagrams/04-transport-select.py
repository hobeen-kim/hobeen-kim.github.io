"""CH04 전송 프로토콜 자동 선택 — 크기와 목적지에 따른 분기 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 26, 18, 12, P["gray"])
    d.text(11, 34, "전송 요청", size=10.5, weight="bold")
    d.text(11, 29.6, "페이로드 · 목적지", size=8.2, color=P["dim"])

    d.box(25, 26, 18, 12, P["chip"])
    d.text(34, 34, "8바이트 이하?", size=10, weight="bold", color=P["accent"])
    d.text(34, 29.6, "크기 판정", size=8.2, color=P["dim"])
    d.arrow(20, 32, 25, 32, color=P["accent"], lw=1.6)

    d.box(25, 43, 18, 10, P["gray"])
    d.text(34, 49.6, "단일 CAN 프레임", size=9.5, weight="bold")
    d.text(34, 46, "8바이트 이하", size=8, color=P["dim"])
    d.arrow(43, 35, 44.5, 46, color=P["accent"], lw=1.5, rad=0.2)
    d.text(40.8, 41, "예", size=8.5, color=P["accent"])

    d.box(48, 26, 18, 12, P["chip"])
    d.text(57, 34, "목적지 지정?", size=10, weight="bold", color=P["accent"])
    d.text(57, 29.6, "브로드캐스트 여부", size=8.2, color=P["dim"])
    d.arrow(43, 32, 48, 32, color=P["accent"], lw=1.6)
    d.text(45.5, 33.8, "아니오", size=8.5, color=P["accent"])

    d.box(72, 42, 25, 11, P["brown"])
    d.text(84.5, 49.4, "TP (BAM)", size=10, weight="bold")
    d.text(84.5, 45.4, "브로드캐스트 · ≤ 1785 바이트", size=8.2, color=P["dim"])
    d.arrow(66, 35, 72, 46, color=P["orange"], lw=1.5, rad=-0.12)

    d.box(72, 27, 25, 11, P["blue"])
    d.text(84.5, 34.4, "TP (연결 모드)", size=10, weight="bold")
    d.text(84.5, 30.4, "목적지 지정 · ≤ 1785 바이트", size=8.2, color=P["dim"])
    d.arrow(66, 32, 72, 32, color=P["accent"], lw=1.5)

    d.box(72, 12, 25, 11, P["green"])
    d.text(84.5, 19.4, "ETP", size=10, weight="bold")
    d.text(84.5, 15.4, "목적지 지정 · > 1785 바이트", size=8.2, color=P["dim"])
    d.arrow(66, 29, 72, 18, color=P["accent"], lw=1.5, rad=0.12)

    d.box(25, 5, 41, 12, P["purple"])
    d.text(45.5, 13, "NMEA 2000 Fast Packet", size=10, weight="bold")
    d.text(45.5, 8.6, "GNSS 등 해당 PGN에 한해 별도 경로 (≤ 223 바이트)",
           size=8.2, color=P["dim"])
    d.arrow(11, 26, 27, 17, color=P["violet"], lw=1.5, rad=0.12, ls="--")


diagram("04-transport-select", draw, w=12, h=6.6, ymax=56)

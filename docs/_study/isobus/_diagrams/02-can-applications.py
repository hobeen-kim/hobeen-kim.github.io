"""CH2 2절 CAN 적용 분야: 자동차, 농기계, 산업기계, 의료장비, 선박, 엘리베이터 (light/dark PNG)."""
from _common import diagram

CARDS = [
    # (분야, 예시 줄, 카드 왼쪽 x, 카드 아래 y, 강조 여부)
    ("자동차", "엔진 제어 · ABS 브레이크\n에어백 시스템 · 계기판\n전동 파워스티어링", 3, 30.5, False),
    ("산업기계", "PLC 제어 · 로봇 관절 제어\n컨베이어 시스템", 3, 16.5, False),
    ("선박", "엔진 모니터링 · 항법 장비", 3, 2.5, False),
    ("농기계", "트랙터 ECU · ISOBUS 작업기\nGPS 자동조향 · 수확량 모니터", 63, 30.5, True),
    ("의료장비", "수술 로봇 · 영상 진단 장비", 63, 16.5, False),
    ("엘리베이터", "층별 제어기 · 도어 제어", 63, 2.5, False),
]
CW, CH = 34, 11.5


def draw(d):
    P = d.P
    ax = d.ax
    cx, cy = 50, 22
    for _, _, x, y, hot in CARDS:
        ex = x + CW if x < cx else x
        ax.plot([cx, ex], [cy, y + CH / 2], color=P["accent"] if hot else P["edge"],
                lw=2.2 if hot else 1.4, zorder=0.5)
    d.box(cx - 9, cy - 4.5, 18, 9, P["purple"])
    d.text(cx, cy, "CAN\n적용 분야", size=12, weight="bold")
    for title, items, x, y, hot in CARDS:
        d.box(x, y, CW, CH, P["green"] if hot else P["gray"],
              ec=P["accent"] if hot else P["edge"], lw=2.0 if hot else 1.4)
        d.text(x + 2, y + CH - 2.4, title, size=12, weight="bold", ha="left")
        d.text(x + 2, y + (CH - 4) / 2, items, size=10.5, ha="left", color=P["text"])


diagram("02-can-applications", draw, w=12, h=5.3, xmax=100, ymax=44)

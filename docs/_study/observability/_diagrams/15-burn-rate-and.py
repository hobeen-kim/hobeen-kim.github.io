"""CH15 multi-window multi-burn-rate — 긴/짧은 윈도 AND 로직 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 두 조건 (좌)
    d.box(4, 34, 32, 8, P["blue"])
    d.text(20, 39.2, "긴 윈도 (지속성)", size=11, weight="bold")
    d.text(20, 36.2, "rate[1h] > threshold", size=9, color=P["dim"])

    d.box(4, 22, 32, 8, P["green"])
    d.text(20, 27.2, "짧은 윈도 (현재성)", size=11, weight="bold")
    d.text(20, 24.2, "rate[5m] > threshold", size=9, color=P["dim"])

    # AND 게이트
    d.box(44, 28, 14, 8, P["gray"], ec=P["accent"], lw=1.8)
    d.text(51, 32, "AND", size=15, weight="bold", color=P["accent"])

    d.arrow(36, 38, 44, 34, color=P["orange"])
    d.arrow(36, 26, 44, 30, color=P["orange"])

    # 결과 (우)
    d.box(66, 34, 30, 8, P["green"], ec=P["accent"], lw=1.6)
    d.text(81, 39.2, "알림 발화", size=12, weight="bold", color=P["accent"])
    d.text(81, 36.2, "둘 다 참", size=9, color=P["dim"])

    d.box(66, 22, 30, 8, P["brown"])
    d.text(81, 27.2, "발화 안 함", size=12, weight="bold", color=P["orange"])
    d.text(81, 24.2, "하나라도 거짓", size=9, color=P["dim"])

    d.arrow(58, 33, 66, 38, color=P["accent"])
    d.arrow(58, 31, 66, 26, color=P["orange"])

    # 단일 윈도 함정 (하단)
    d.box(6, 6, 42, 9, P["purple"])
    d.text(27, 11.6, "긴 윈도만 → 반응 지연", size=10.5, weight="bold", color=P["violet"])
    d.text(27, 8.4, "장애 뒤 알림이 너무 늦음", size=8.5, color=P["dim"])

    d.box(52, 6, 42, 9, P["purple"])
    d.text(73, 11.6, "짧은 윈도만 → 오탐", size=10.5, weight="bold", color=P["violet"])
    d.text(73, 8.4, "순간 스파이크에도 알림", size=8.5, color=P["dim"])


diagram("15-burn-rate-and", draw, w=12, h=5.6, ymax=46)

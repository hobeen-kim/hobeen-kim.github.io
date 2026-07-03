"""CH02 신호 상관관계 — exemplar·라벨로 신호를 잇는 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(3, 18, 22, 12, P["blue"])
    d.text(14, 26.4, "메트릭", size=12, weight="bold")
    d.text(14, 22.6, "레이턴시 스파이크 감지", size=8.5, color=P["dim"])

    d.box(39, 18, 22, 12, P["green"], ec=P["accent"], lw=1.8)
    d.text(50, 26.4, "트레이스", size=12, weight="bold", color=P["accent"])
    d.text(50, 22.6, "느린 span 특정", size=8.5, color=P["dim"])

    d.box(75, 28, 22, 12, P["brown"])
    d.text(86, 36.4, "로그", size=12, weight="bold")
    d.text(86, 32.6, "에러 상세 확인", size=8.5, color=P["dim"])

    d.box(75, 6, 22, 12, P["purple"])
    d.text(86, 14.4, "프로파일", size=12, weight="bold")
    d.text(86, 10.6, "코드 레벨 병목", size=8.5, color=P["dim"])

    d.arrow(25, 24, 39, 24, color=P["orange"])
    d.text(32, 26, "exemplar", size=8, color=P["orange"])

    d.arrow(61, 25.5, 75, 32, color=P["accent"], rad=0.12)
    d.text(68.5, 31.2, "trace_id 라벨", size=8, color=P["accent"])

    d.arrow(61, 22.5, 75, 13, color=P["violet"], rad=-0.12)
    d.text(67.5, 15.4, "span 컨텍스트", size=8, color=P["violet"])


diagram("02-signal-correlation", draw, w=13, h=5.4, ymax=46)

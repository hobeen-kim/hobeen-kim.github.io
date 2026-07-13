"""CH13 thermal 파이프라인 — 센서에서 스로틀링·통지까지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 커널 계층
    d.box(4, 30, 22, 10, P["brown"])
    d.text(15, 35, "온도 센서\n(SoC·배터리·PCB)", size=8.8, weight="bold")

    d.box(32, 30, 24, 10, P["gray"])
    d.text(44, 35, "커널 thermal zone\ntrip point·governor", size=8.8, weight="bold")

    d.arrow(26, 35, 32, 35, color=P["accent"], lw=1.3)

    # HAL·서비스 계층
    d.box(62, 30, 22, 10, P["green"])
    d.text(73, 35, "Thermal HAL\n(AIDL)", size=9, weight="bold")

    d.box(62, 14, 22, 10, P["purple"])
    d.text(73, 19, "ThermalService\nthrottling status", size=8.8, weight="bold")

    d.arrow(56, 35, 62, 35, color=P["accent"], lw=1.3)
    d.arrow(73, 30, 73, 24, color=P["accent"], lw=1.3)

    # 스로틀링 액션 (아래 왼쪽)
    actions = [
        ("cpufreq 제한", P["blue"]),
        ("GPU 클럭 down", P["blue"]),
        ("충전 전류 제한", P["brown"]),
        ("셧다운(임계)", P["gray"]),
    ]
    for i, (a, fc) in enumerate(actions):
        x = 4 + (i % 2) * 26
        y = 14 - (i // 2) * 6.5
        d.box(x, y, 24, 5.5, fc)
        d.text(x + 12, y + 2.7, a, size=8.5)

    d.arrow(44, 30, 30, 14, color=P["orange"], lw=1.3, rad=0.1)
    d.text(34, 24, "쿨링 디바이스", size=8, color=P["orange"])

    # 앱 통지
    d.box(88, 14, 10, 10, P["chip"])
    d.text(93, 19, "앱\n통지", size=8.5, color=P["dim"])
    d.arrow(84, 19, 88, 19, color=P["violet"], lw=1.2)


diagram("13-thermal", draw, w=12, h=5.6, ymax=44)

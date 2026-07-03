"""CH28 Alloy 프로세스 내부 구조 — 구문 + 실행 엔진 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 바깥 Alloy 프로세스
    d.box(5, 5, 90, 34, P["chip"], ec=P["accent"], lw=2.0)
    d.text(50, 36.6, "Alloy 프로세스 (단일 바이너리)", size=12,
           weight="bold", color=P["accent"])

    # Alloy 구문 (상단)
    d.box(30, 29, 40, 5.5, P["purple"])
    d.text(50, 31.75, "Alloy 구문 (구 River · 컴포넌트 그래프)", size=10, weight="bold")

    # 실행 엔진 그룹
    d.box(8, 8, 84, 17, P["gray"])
    d.text(50, 22.7, "실행 엔진", size=10.5, weight="bold", color=P["dim"])

    cores = [
        ("OpenTelemetry\nCollector 코드베이스", "otelcol.*", P["blue"]),
        ("Prometheus\n클라이언트", "prometheus.*", P["green"]),
        ("Loki\n클라이언트", "loki.*", P["brown"]),
        ("Pyroscope\n클라이언트", "pyroscope.*", P["purple"]),
    ]
    cw = 19
    xs = [10.5, 31, 51.5, 72]
    for (t, pre, col), x in zip(cores, xs):
        d.box(x, 9.5, cw, 10, col)
        d.text(x + cw / 2, 14.3, t, size=8.8, weight="bold")
        d.text(x + cw / 2, 11.2, pre, size=8.6, color=P["accent"], style="italic")
        d.arrow(50, 29, x + cw / 2, 19.5, color=P["orange"], lw=1.5)


diagram("28-alloy-process", draw, w=13, h=5.8, ymax=40)

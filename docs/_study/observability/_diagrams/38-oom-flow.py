"""CH38 Prometheus OOM Kill — 진단에서 재발 방지까지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(cx, cy, w, h, title, sub, fc, ec=None):
        d.box(cx - w / 2, cy - h / 2, w, h, fc, ec=ec)
        if sub:
            d.text(cx, cy + h * 0.16, title, size=10.5, weight="bold")
            d.text(cx, cy - h * 0.24, sub, size=8, color=P["dim"])
        else:
            d.text(cx, cy, title, size=10.5, weight="bold")

    node(50, 45, 34, 6.5, "Prometheus OOM Kill", "process_resident_memory > limit", P["brown"], ec=P["orange"])
    node(50, 37, 32, 6.5, "head_series 추세 확인", "현재 활성 시계열 수", P["gray"], ec=P["accent"])

    node(26, 28, 26, 6.5, "topk로 폭증 원인 좁히기", "어떤 job·metric이 폭증?", P["blue"])
    node(78, 28, 22, 6.5, "단순 용량 부족", "리소스 증설 검토", P["gray"])

    node(26, 20, 26, 6, "즉각 조치 (임시)", "metricRelabelings drop", P["green"])
    node(26, 12, 26, 6, "Prometheus 재시작", "head block 초기화", P["gray"])

    node(63, 20, 26, 6, "근본 조치", "계측에서 고유값 라벨 제거", P["green"], ec=P["accent"])
    node(63, 12, 26, 6, "재발 방지", "sample_limit · label_limit", P["blue"])

    d.arrow(50, 41.75, 50, 40.25, color=P["accent"])
    d.arrow(43, 34.5, 31, 31, color=P["orange"], lw=1.7, rad=-0.05)
    d.text(34, 33.2, "급증", size=8, color=P["orange"], weight="bold")
    d.arrow(57, 34.5, 73, 31, color=P["dim"], lw=1.6, rad=0.05)
    d.text(67, 33.2, "완만", size=8, color=P["dim"], weight="bold")

    d.arrow(26, 24.75, 26, 23, color=P["accent"], lw=1.7)
    d.arrow(26, 17, 26, 15, color=P["accent"], lw=1.7)
    d.arrow(39, 20, 50, 20, color=P["accent"], lw=1.7)
    d.text(44.5, 21.8, "이후", size=8, color=P["dim"])
    d.arrow(63, 17, 63, 15, color=P["accent"], lw=1.7)


diagram("38-oom-flow", draw, w=12, h=5.6, ymax=50)

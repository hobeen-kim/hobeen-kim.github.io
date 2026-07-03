"""CH06 §1 시계열 식별 — metric name + 라벨 집합 = 유일 ID (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽: metric name + 라벨들
    d.box(3, 40, 27, 6, P["gray"], ec=P["accent"], lw=1.8)
    d.text(16.5, 43, "__name__\nhttp_requests_total", size=9.5, color=P["accent"])

    labels = [
        ('method="GET"',             P["blue"]),
        ('status="200"',             P["green"]),
        ('job="api"',                P["brown"]),
        ('instance="10.0.0.5:8080"', P["purple"]),
    ]
    for i, (t, col) in enumerate(labels):
        yy = 32 - i * 7.5
        d.box(3, yy, 27, 5.5, col)
        d.text(16.5, yy + 2.75, t, size=10)

    # 중앙: 유일 ID
    d.box(43, 17, 24, 14, P["chip"], ec=P["accent"], lw=1.8)
    d.text(55, 26, "라벨 집합 조합\n= 유일한 시계열 ID", size=11, weight="bold",
           color=P["accent"])
    d.text(55, 20, "값 하나만 바뀌어도\n별개의 시계열", size=8.5, color=P["dim"])

    # 오른쪽: 샘플 스트림
    d.box(76, 18, 21, 12, P["brown"])
    d.text(86.5, 24, "샘플 스트림\n(t1,v1) (t2,v2) …", size=9.5)

    # 화살표
    for yy in [43, 34.75, 27.25, 19.75, 12.25]:
        d.arrow(30, yy, 43, 24, color=P["dim"], lw=1.4)
    d.arrow(67, 24, 76, 24, color=P["accent"])
    d.text(71.5, 25.6, "append", size=8, color=P["accent"])


diagram("06-timeseries-id", draw, w=13, h=6.4, ymax=48)

"""CH13 Alertmanager 알림 파이프라인 단계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("Prometheus로부터 알림 수신", "", P["gray"], P["edge"]),
        ("Deduplicate", "동일 fingerprint 알림 병합", P["blue"], P["accent"]),
        ("Group", "group_by 라벨 기준 묶음", P["blue"], P["accent"]),
        ("Inhibit", "더 심각한 알림이 있으면 하위 알림 억제", P["brown"], P["orange"]),
        ("Silence", "matcher에 걸리면 완전 차단", P["brown"], P["orange"]),
        ("Route", "route 트리 따라 receiver 결정", P["green"], P["accent"]),
        ("Notify", "receiver별 채널로 전송, 실패 시 재시도", P["green"], P["accent"]),
    ]
    n = len(stages)
    top = 45
    gap = 6.2
    bw, bh = 52, 4.6
    for i, (t, sub, fc, ec) in enumerate(stages):
        yc = top - i * gap
        d.box(50 - bw / 2, yc - bh / 2, bw, bh, fc, ec=ec, lw=1.6)
        if sub:
            d.text(38, yc, t, size=10.5, weight="bold", ha="left")
            d.text(90, yc, sub, size=8.2, color=P["dim"], ha="right")
        else:
            d.text(50, yc, t, size=10.5, weight="bold")
        if i < n - 1:
            d.arrow(50, yc - bh / 2, 50, yc - gap + bh / 2, color=P["accent"])

    # 그룹 라벨 (우측)
    d.text(89, top - 1.5 * gap, "중복 제거·묶음", size=8.5, color=P["accent"],
           weight="bold", ha="left")
    d.text(89, top - 3.5 * gap, "억제·차단", size=8.5, color=P["orange"],
           weight="bold", ha="left")
    d.text(89, top - 5.5 * gap, "라우팅·전송", size=8.5, color=P["accent"],
           weight="bold", ha="left")


diagram("13-pipeline", draw, w=12, h=7.5, ymax=50)

"""CH07 §3 서비스 디스커버리 — SD 소스 → Discovery Manager → Retrieval (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 상단: SD 소스 4종
    sds = [
        (P["blue"],   "kubernetes_sd_configs", "__meta_kubernetes_*"),
        (P["green"],  "ec2_sd_configs",        "__meta_ec2_*"),
        (P["brown"],  "consul_sd_configs",     "__meta_consul_*"),
        (P["purple"], "file_sd_configs",       "GitOps 친화적"),
    ]
    xs = [2, 26, 50, 74]
    for x, (col, title, meta) in zip(xs, sds):
        d.box(x, 34, 22, 11, col)
        cx = x + 11
        d.text(cx, 41, title, size=9.5, weight="bold")
        d.text(cx, 37, meta, size=8, color=P["accent"])

    # 중앙: Discovery Manager
    d.box(31, 19, 38, 9, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 23.5, "Discovery Manager\n타깃 목록 통합 관리", size=10.5,
           weight="bold", color=P["accent"])

    # 하단: Retrieval
    d.box(37, 5, 26, 8, P["chip"], ec=P["orange"], lw=1.5)
    d.text(50, 9, "Retrieval\nrelabel 적용 후 스크레이프", size=10, color=P["orange"])

    # 화살표
    for x in xs:
        cx = x + 11
        tx = 50 + (cx - 50) * 0.4
        d.arrow(cx, 34, tx, 28, color=P["accent"], lw=1.6)
    d.arrow(50, 19, 50, 13, color=P["orange"])
    d.text(58, 16, "relabel 적용", size=8, color=P["orange"])


diagram("07-service-discovery", draw, w=12, h=6, ymax=48)

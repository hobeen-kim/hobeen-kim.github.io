"""CH28 Alloy Cluster — gossip + 컨시스턴트 해싱 타깃 분배 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽: discovery 타깃
    d.box(2, 14, 20, 12, P["blue"])
    d.text(12, 21.5, "discovery.\nkubernetes", size=10, weight="bold")
    d.text(12, 16.6, "타깃 N개", size=9, color=P["dim"])

    # 중앙: 클러스터
    d.box(29, 6, 42, 28, P["gray"], ec=P["accent"], lw=2.0)
    d.text(50, 31.3, "Alloy Cluster (StatefulSet · 3 replica)", size=10,
           weight="bold", color=P["accent"])

    reps = [(34, 22), (54, 22), (44, 11)]
    rw, rh = 13, 6.5
    for x, y in reps:
        d.box(x, y, rw, rh, P["green"])
    d.text(34 + rw / 2, 22 + rh / 2, "alloy-0", size=10, weight="bold")
    d.text(54 + rw / 2, 22 + rh / 2, "alloy-1", size=10, weight="bold")
    d.text(44 + rw / 2, 11 + rh / 2, "alloy-2", size=10, weight="bold")

    # gossip (양방향, 박스 사이 여백)
    d.arrow(47, 25.2, 54, 25.2, color=P["orange"], lw=1.6, style="<|-|>")
    d.arrow(41, 22, 47, 17.5, color=P["orange"], lw=1.6, style="<|-|>")
    d.arrow(60, 22, 54, 17.5, color=P["orange"], lw=1.6, style="<|-|>")
    d.text(50.5, 27, "gossip", size=8.5, color=P["orange"], weight="bold")

    # discovery -> cluster
    d.arrow(22, 20, 29, 20, color=P["accent"], lw=2.0)
    d.text(25.5, 23, "컨시스턴트\n해싱 분배", size=8, color=P["accent"], weight="bold")

    # 오른쪽: 백엔드
    d.box(78, 14, 20, 12, P["brown"])
    d.text(88, 21.5, "Mimir / Loki\n/ Tempo", size=9.5, weight="bold")
    d.text(88, 16.6, "자기 몫만 write", size=8.3, color=P["dim"])

    d.arrow(71, 20, 78, 20, color=P["accent"], lw=2.0)
    d.text(74.5, 22.6, "remote_write", size=8, color=P["dim"])


diagram("28-clustering", draw, w=13, h=5.6, ymax=38)

"""CH29 clustering 타깃 분배 — 시퀀스 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    actors = [(16, "discovery.\nkubernetes", P["blue"]),
              (50, "Alloy Cluster\n(3 replica)", P["green"]),
              (86, "Mimir", P["brown"])]
    top, bot = 41, 5
    for x, name, col in actors:
        d.box(x - 12, top, 24, 5.5, col, ec=P["accent"], lw=1.5)
        d.text(x, top + 2.75, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [bot, top], color=P["edge"], lw=1.3,
                  ls=(0, (4, 3)), zorder=1)

    xD, xC, xM = 16, 50, 86

    # 1. discovery -> cluster
    d.arrow(xD, 38, xC - 12, 38, color=P["accent"], lw=1.9)
    d.text((xD + xC) / 2 - 6, 39.4, "타깃 200개 발견", size=8.5, weight="bold")

    # 2. note: 컨시스턴트 해싱 소유권 분배
    d.box(xC - 22, 22, 44, 12, P["chip"], ec=P["orange"], lw=1.4)
    d.text(xC, 31.6, "컨시스턴트 해싱 → 소유권 분배", size=9,
           color=P["orange"], weight="bold")
    d.text(xC, 28.3, "alloy-0 · 타깃 1 ~ 67", size=8.5)
    d.text(xC, 26.0, "alloy-1 · 타깃 68 ~ 134", size=8.5)
    d.text(xC, 23.7, "alloy-2 · 타깃 135 ~ 200", size=8.5)

    # 3. cluster -> Mimir
    d.arrow(xC + 12, 18, xM, 18, color=P["accent"], lw=1.9)
    d.text((xC + xM) / 2 + 6, 19.4, "각 레플리카가 자기 몫만 remote_write",
           size=8.3, weight="bold")

    # 4. note: 장애 재조정
    d.box(xC - 22, 8, 44, 5, P["brown"], ec=P["orange"], lw=1.4)
    d.text(xC, 10.5, "alloy-1 다운 → 나머지가 재해싱해 흡수", size=8.6,
           color=P["orange"], weight="bold")


diagram("29-clustering-sequence", draw, w=13, h=6.4, ymax=48)

"""CH47 §1 task total과 lifetime total의 시간 흐름: 시작, 일시정지, 재개(리셋 후 복원), 완료 (light/dark PNG)."""
from _common import diagram

X_START, X_PAUSE, X_RESUME, X_DONE, X_END = 16, 44, 62, 88, 95
TOP_BASE, BOT_BASE, PANEL_H = 29, 5, 16
TASK_MAX = 5
LIFE_MIN, LIFE_MAX = 1195, 1200

EVENTS = [(X_START, "시작\n(0→1)"), (X_PAUSE, "일시정지\n(1→0)"),
          (X_RESUME, "재개\n(0→1)"), (X_DONE, "완료\n(1→0)")]


def ty(v):
    return TOP_BASE + PANEL_H * v / TASK_MAX


def ly(v):
    return BOT_BASE + PANEL_H * (v - LIFE_MIN) / (LIFE_MAX - LIFE_MIN)


def draw(d):
    P = d.P
    for base in (TOP_BASE, BOT_BASE):
        d.arrow(12, base, 97, base, color=P["edge"], lw=1.1, style="-")
    for x, label in EVENTS:
        d.ax.plot([x, x], [BOT_BASE, ty(TASK_MAX) + 1.0], color=P["edge"], lw=1.0,
                  ls=":", zorder=2)
        d.text(x, ty(TASK_MAX) + 3.6, label, size=8.5, color=P["dim"])
    d.text(97, TOP_BASE - 1.6, "시간", size=8.5, color=P["dim"], ha="right")

    for v in (0, 3, 5):
        d.text(11, ty(v), str(v), size=8.5, color=P["dim"], ha="right")
    for v in (1195, 1198, 1200):
        d.text(11, ly(v), f"{v:,}", size=8.5, color=P["dim"], ha="right")
    d.text(18, ty(TASK_MAX) - 1.0, "task total (ha)", size=9.5, ha="left")
    d.text(18, ly(LIFE_MAX) - 1.0, "lifetime total (ha)", size=9.5, ha="left")

    d.ax.plot([X_START, X_PAUSE, X_RESUME], [ty(0), ty(3), ty(3)],
              color=P["accent"], lw=2.2, zorder=4)
    d.ax.plot([X_RESUME, X_RESUME], [ty(3), ty(0)], color=P["orange"], lw=1.6,
              ls="--", zorder=4)
    d.ax.plot([X_RESUME], [ty(0)], marker="o", markersize=7, color=P["orange"], zorder=5)
    d.arrow(X_RESUME + 1.2, ty(0) + 0.3, X_RESUME + 1.2, ty(3) - 0.2, color=P["violet"], lw=1.6)
    d.ax.plot([X_RESUME + 1.2, X_DONE, X_END], [ty(3), ty(5), ty(5)],
              color=P["accent"], lw=2.2, zorder=4)
    d.text(X_RESUME - 1.0, ty(1.0), "클라이언트가\n0으로 리셋", size=8, color=P["orange"], ha="right")
    d.text(X_RESUME + 2.6, ty(1.0), "TC가 저장값 3 ha를\nValue command로 복원", size=8,
           color=P["violet"], ha="left")
    d.text((X_PAUSE + X_RESUME) / 2, ty(3) + 1.6, "TC가 3 ha를 받아 저장", size=8, color=P["dim"])

    d.ax.plot([X_START, X_PAUSE, X_RESUME, X_DONE, X_END],
              [ly(1195), ly(1198), ly(1198), ly(1200), ly(1200)],
              color=P["orange"], lw=2.2, zorder=4)


diagram("47-total-counters", draw, w=12, h=6.0, xmax=100, ymax=50)

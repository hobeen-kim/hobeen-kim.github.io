"""CH13 suspend/wakelock 구조 — 유저스페이스와 커널 양면 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 유저스페이스 영역
    d.box(3, 26, 94, 18, P["chip"])
    d.text(9, 41.5, "유저스페이스", size=9, weight="bold", color=P["dim"], ha="left")

    d.box(6, 29, 24, 10, P["blue"])
    d.text(18, 34, "앱 / 서비스\nPowerManager.WakeLock", size=8.8, weight="bold")

    d.box(38, 29, 26, 10, P["purple"])
    d.text(51, 34, "PowerManagerService\nwakelock 집계·doze·idle", size=8.6, weight="bold")

    d.box(72, 29, 22, 10, P["green"])
    d.text(83, 34, "SystemSuspend\n(libsuspend/HAL)", size=8.8, weight="bold")

    d.arrow(30, 34, 38, 34, color=P["accent"], lw=1.3)
    d.arrow(64, 34, 72, 34, color=P["accent"], lw=1.3)

    # 커널 영역
    d.box(3, 4, 94, 18, P["gray"])
    d.text(9, 19.5, "커널", size=9, weight="bold", color=P["dim"], ha="left")

    d.box(10, 7, 26, 9, P["brown"])
    d.text(23, 11.5, "/sys/power/wake_lock\nwakeup_source", size=8.6, weight="bold")

    d.box(42, 7, 22, 9, P["brown"])
    d.text(53, 11.5, "autosleep\n(모든 wakelock 해제 시)", size=8.4, weight="bold")

    d.box(70, 7, 24, 9, P["blue"])
    d.text(82, 11.5, "suspend_ops\n→ suspend / resume", size=8.6, weight="bold")

    d.arrow(83, 29, 23, 16, color=P["orange"], lw=1.3, rad=0.1)
    d.text(50, 24, "epoll → sysfs 기록", size=8, color=P["orange"])
    d.arrow(36, 11.5, 42, 11.5, color=P["accent"], lw=1.3)
    d.arrow(64, 11.5, 70, 11.5, color=P["accent"], lw=1.3)


diagram("13-suspend-flow", draw, w=12, h=5.8, ymax=46)

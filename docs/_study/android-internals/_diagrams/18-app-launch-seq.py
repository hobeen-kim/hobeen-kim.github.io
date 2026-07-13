"""CH18 앱 시작 시퀀스 — Launcher 탭에서 첫 프레임까지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    lanes = [
        ("Launcher", 12, P["blue"]),
        ("system_server\n(ATMS/AMS)", 34, P["green"]),
        ("Zygote", 56, P["brown"]),
        ("앱 프로세스", 82, P["purple"]),
    ]
    for name, x, fc in lanes:
        d.box(x - 9, 43, 18, 5, fc)
        d.text(x, 45.5, name, size=8.6, weight="bold")
        d.arrow(x, 43, x, 5, color=P["edge"], lw=1.1, style="-")

    def msg(x1, x2, y, label, color=None):
        d.arrow(x1, y, x2, y, color=color or P["accent"], lw=1.6)
        mid = (x1 + x2) / 2
        d.text(mid, y + 1.1, label, size=7.4, color=P["dim"])

    msg(12, 34, 39, "startActivity() (Binder)")
    msg(34, 56, 33, "socket: fork 요청", P["orange"])
    d.text(56, 29.5, "fork() + specialize", size=7.4, color=P["dim"])
    msg(56, 82, 27, "새 프로세스", P["orange"])
    msg(82, 34, 21, "attachApplication() (Binder)", P["violet"])
    msg(34, 82, 15, "bindApplication → onCreate", P["violet"])
    d.text(82, 11.5, "Activity.onCreate\n→ onStart → onResume", size=7.6,
           color=P["dim"])
    d.text(82, 6.5, "첫 프레임 렌더", size=7.8, weight="bold", color=P["accent"])


diagram("18-app-launch-seq", draw, w=12.5, h=6.2, ymax=50)

"""CH11 cgroup·태스크 프로파일 — 스케줄링 그룹 배치 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # cgroup v2 루트
    d.box(36, 40, 28, 7, P["gray"], ec=P["accent"], lw=1.6)
    d.text(50, 43.5, "cgroup v2 루트\n(/sys/fs/cgroup)", size=9.5,
           weight="bold", color=P["accent"])

    groups = [
        ("top-app", "포그라운드 상호작용 앱\ncpuset=대형코어, uclamp↑", P["green"], 2),
        ("foreground", "보이는 서비스\n중간 우선순위", P["blue"], 27),
        ("background", "백그라운드 앱\ncpuset=소형코어", P["brown"], 52),
        ("system-background", "시스템 데몬\n제한적 코어", P["purple"], 77),
    ]
    for name, sub, fc, x in groups:
        d.box(x, 18, 21, 14, fc)
        d.text(x + 10.5, 28.5, name, size=10, weight="bold")
        d.text(x + 10.5, 22.5, sub, size=8, color=P["dim"])
        d.arrow(50, 40, x + 10.5, 32, color=P["accent"], lw=1.2, rad=0.05)

    # task_profiles.json 매핑
    d.box(14, 4, 72, 7, P["chip"])
    d.text(50, 7.5, "task_profiles.json — 프로파일명 → 컨트롤러(cpuset·schedtune/uclamp·cpu.shares) 매핑",
           size=9, color=P["dim"])
    for x in (12.5, 37.5, 62.5, 87.5):
        d.arrow(x, 18, x - (x - 50) * 0.15, 11, color=P["orange"], lw=1.1, rad=0)


diagram("11-cgroup-hierarchy", draw, w=12, h=6, ymax=48)

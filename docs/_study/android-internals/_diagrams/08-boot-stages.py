"""CH8 init 부트 트리거 단계 흐름 — early-init부터 boot까지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("early-init", "ueventd·SELinux 준비", P["gray"]),
        ("init", "기본 dir·심볼릭 링크", P["gray"]),
        ("late-init", "이후 트리거 큐잉", P["gray"]),
        ("fs", "fstab 마운트", P["blue"]),
        ("post-fs", "/vendor 등 접근 가능", P["blue"]),
        ("post-fs-data", "/data 복호화·마운트", P["brown"]),
        ("zygote-start", "Zygote·servicemanager", P["purple"]),
        ("boot", "부팅 완료 액션", P["green"]),
    ]

    x, w, h, gap = 30, 40, 6.6, 2.4
    top = 88
    ys = [top - i * (h + gap) for i in range(len(stages))]

    for i, ((title, sub, fc), y) in enumerate(zip(stages, ys)):
        hl = title in ("post-fs-data", "zygote-start")
        d.box(x, y, w, h, fc, ec=P["accent"] if hl else None,
              lw=1.8 if hl else 1.4)
        d.text(x + w * 0.30, y + h / 2, "on " + title, size=10, weight="bold")
        d.text(x + w * 0.74, y + h / 2, sub, size=8.3, color=P["dim"])
        if i < len(stages) - 1:
            d.arrow(x + w / 2, y, x + w / 2, ys[i + 1] + h, color=P["accent"])

    # 곁가지 주석
    d.text(x - 2, ys[5] + h / 2, "vold가\n키 언락", size=8, color=P["orange"],
           ha="right")
    d.text(x + w + 2, ys[6] + h / 2, "여기서\nCAN 데몬\nstart 가능", size=8,
           color=P["orange"], ha="left")


diagram("08-boot-stages", draw, w=8.5, h=9.5, xmax=100, ymax=100)

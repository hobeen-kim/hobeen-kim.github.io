"""CH6 boot.img 버전별 구조 — v0~v2 통합형에서 v3/v4 GKI 분리형으로."""
from _common import diagram


def draw(d):
    P = d.P

    # 좌: 레거시 boot.img (v0~v2)
    d.text(22, 45, "boot.img v0~v2 (통합형)", size=10, weight="bold",
           color=P["accent"])
    legacy = [
        ("boot header", P["gray"], 4),
        ("kernel", P["blue"], 9),
        ("ramdisk (init + 벤더 리소스 혼재)", P["brown"], 14),
        ("second / dtb (선택)", P["purple"], 6),
    ]
    y = 38
    for label, fc, h in legacy:
        d.box(6, y - h, 32, h - 1, fc)
        d.text(22, y - h / 2, label, size=8.5)
        y -= h

    # 우: GKI 분리형 (v3/v4 + vendor_boot + init_boot)
    d.text(72, 45, "GKI 분리형 (v3/v4, Android 11+ / 13+)", size=10,
           weight="bold", color=P["accent"])
    gki = [
        ("boot.img", "GKI 커널 + boot header", P["blue"], 34, 9),
        ("init_boot.img", "generic ramdisk (init)  · 13+", P["green"], 24, 8),
        ("vendor_boot.img", "vendor ramdisk + DTB\n+ vendor_ramdisk_table", P["brown"], 12, 10),
    ]
    for name, desc, fc, yy, h in gki:
        d.box(56, yy, 38, h, fc)
        d.text(75, yy + h - 2, name, size=9, weight="bold", color=P["accent"])
        d.text(75, yy + h / 2 - 1.5, desc, size=8, color=P["dim"])

    d.arrow(40, 22, 55, 26, color=P["orange"], rad=0.1)
    d.text(47, 27, "커널/벤더 분리\n(update_engine 개별 갱신)", size=8,
           color=P["orange"], ha="center")


diagram("06-boot-img", draw, w=12, h=6, ymax=48)

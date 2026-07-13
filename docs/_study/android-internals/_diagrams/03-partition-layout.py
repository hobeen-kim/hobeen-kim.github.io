"""CH3 파티션 레이아웃 — A/B 슬롯 물리 파티션과 super 안의 동적(논리) 파티션."""
from _common import diagram


def draw(d):
    P = d.P

    # 물리 파티션 행 (플래시 스토리지 위)
    d.text(50, 46.5, "플래시 스토리지 (eMMC / UFS) — GPT", size=11,
           weight="bold", color=P["accent"])

    phys = [
        (4, 10, "bootloader", P["chip"]),
        (15, 8, "boot_a", P["blue"]),
        (24, 8, "boot_b", P["blue"]),
        (33, 9, "vbmeta_a", P["purple"]),
        (43, 9, "vbmeta_b", P["purple"]),
        (53, 8, "misc\n(BCB)", P["gray"]),
        (63, 29, "super", P["green"]),
    ]
    for x, w, label, fc in phys:
        d.box(x, 37, w, 7, fc)
        d.text(x + w / 2, 40.5, label, size=9)

    # super → 동적 파티션 컨테이너 연결
    d.arrow(77, 37, 57, 28.5, color=P["orange"], rad=-0.15)
    d.text(70, 32, "liblp / lpdump", size=8, color=P["orange"])

    # 동적 파티션 컨테이너
    d.box(6, 4, 88, 24, P["gray"], ec=P["accent"], lw=1.6)
    d.text(50, 25.5, "super.img — 동적 파티션 (하나의 물리 파티션 안 논리 볼륨)",
           size=10, weight="bold", color=P["accent"])

    slots = [("슬롯 A", "_a", 10), ("슬롯 B", "_b", 52)]
    parts = ["system", "vendor", "product", "system_ext"]
    colors = [P["blue"], P["brown"], P["purple"], P["chip"]]
    for title, suf, x0 in slots:
        d.text(x0 + 18, 21.5, title, size=9, weight="bold", color=P["dim"])
        for i, (name, fc) in enumerate(zip(parts, colors)):
            y = 16.5 - i * 4.3
            d.box(x0, y, 36, 3.6, fc)
            d.text(x0 + 18, y + 1.8, f"{name}{suf}", size=9)


diagram("03-partition-layout", draw, w=12, h=6.4, ymax=48)

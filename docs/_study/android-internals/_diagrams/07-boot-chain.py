"""CH7 부트체인 — Boot ROM부터 init까지 서명으로 이어지는 신뢰 체인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("Boot ROM (PBL)", "SoC 내장 · 불변\n루트 오브 트러스트", P["gray"]),
        ("2차 부트로더", "Qualcomm XBL/UEFI\nSamsung S-BOOT\nMTK Preloader", P["blue"]),
        ("Android Bootloader", "ABL / LK\nfastboot · boot.img 로드", P["brown"]),
        ("Linux Kernel", "cmdline · DTB\ninitramfs 언팩", P["green"]),
        ("init (PID 1)", "유저스페이스\n첫 프로세스", P["purple"]),
    ]

    x, w, h, gap = 2, 17, 20, 2.75
    y = 16
    xs = [x + i * (w + gap) for i in range(len(stages))]

    for i, ((title, sub, fc), xi) in enumerate(zip(stages, xs)):
        d.box(xi, y, w, h, fc, ec=P["accent"] if i == 0 else None,
              lw=1.8 if i == 0 else 1.4)
        d.text(xi + w / 2, y + h * 0.72, title, size=10.5, weight="bold")
        d.text(xi + w / 2, y + h * 0.32, sub, size=8.3, color=P["dim"])
        if i < len(stages) - 1:
            d.arrow(xi + w, y + h / 2, xs[i + 1], y + h / 2, color=P["accent"])

    # 신뢰 체인 라벨: 각 단계가 다음 단계 서명을 검증
    for i in range(len(stages) - 1):
        mx = (xs[i] + w + xs[i + 1]) / 2
        d.text(mx, y + h + 1.6, "검증\n+로드", size=7.5, color=P["orange"])

    d.text(2, y - 4.5, "각 단계는 다음 단계의 서명을 검증한 뒤에만 실행을 넘긴다 (Chain of Trust)",
           size=9, color=P["dim"], ha="left")


diagram("07-boot-chain", draw, w=13, h=5, xmax=100, ymax=42)

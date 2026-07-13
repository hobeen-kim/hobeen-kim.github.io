"""README 학습 로드맵 — 7개 섹션의 학습 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    sections = [
        ("S1 · 아키텍처와 하드웨어", "CH1~2 — 스택 조감 · SoC · Device Tree", P["blue"]),
        ("S2 · 파티션·스토리지·이미지", "CH3~6 — 파티션 · 파일시스템 · APEX · OTA", P["green"]),
        ("S3 · 부팅과 시스템 기동", "CH7~8 — 부트로더 · 커널 · init · Zygote", P["brown"]),
        ("S4 · 시스템 관리와 관찰", "CH9~13 — 서비스 · 설정 · 로깅 · 전원", P["purple"]),
        ("S5 · AOSP 빌드와 네이티브", "CH14~16 — 소스 빌드 · Bionic · SELinux·AVB", P["blue"]),
        ("S6 · 패키지·앱·런타임", "CH17~20 — 패키지 · APK · DEX · ART", P["green"]),
        ("S7 · Binder와 실전", "CH21~23 — Binder 유저·커널 · 네이티브 데몬", P["brown"]),
    ]

    x, w, h, gap = 20, 60, 10, 3.0
    top = 85
    ys = [top - i * (h + gap) for i in range(len(sections))]

    for i, ((title, sub, fc), y) in enumerate(zip(sections, ys)):
        d.box(x, y, w, h, fc, ec=P["accent"] if i == 0 else None,
              lw=1.8 if i == 0 else 1.4)
        d.text(x + w / 2, y + h * 0.63, title, size=12, weight="bold")
        d.text(x + w / 2, y + h * 0.27, sub, size=9.5, color=P["dim"])
        if i < len(sections) - 1:
            d.arrow(x + w / 2, y, x + w / 2, ys[i + 1] + h, color=P["accent"])

    # 곁가지: AOSP 급하면 S5부터 진입 가능 안내 화살표
    d.arrow(x, ys[0] + h / 2, x - 6, ys[4] + h / 2, color=P["orange"],
            rad=-0.55, ls="--", lw=1.5)
    d.text(x - 11, (ys[0] + ys[4]) / 2 + h / 2, "AOSP\n급하면\nCH14부터", size=8.5,
           color=P["orange"])


diagram("00-roadmap", draw, w=9, h=11, xmax=100, ymax=100)

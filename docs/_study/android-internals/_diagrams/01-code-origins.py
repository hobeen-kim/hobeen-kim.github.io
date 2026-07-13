"""CH1 코드 출처 — 기기 이미지를 이루는 레이어들의 합성 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    sources = [
        ("AOSP", "코어 프레임워크 · ART · init · Bionic", P["blue"]),
        ("AOSP external/", "오픈소스 3rd party (upstream libc++·boringssl 등)", P["blue"]),
        ("Linux Kernel", "GKI + 안드로이드 패치", P["gray"]),
        ("Platform / BSP (vendor)", "SoC 벤더 blob · HAL · 펌웨어 (Qualcomm·MediaTek)", P["brown"]),
        ("ODM", "보드 제조사 튜닝 · 센서/카메라 캘리브레이션", P["green"]),
        ("Carrier", "통신사 커스터마이징 · 사전 탑재 앱", P["purple"]),
    ]

    x, w, h, gap = 4, 40, 8.5, 2.2
    top = 82
    ys = [top - i * (h + gap) for i in range(len(sources))]

    for (title, sub, fc), y in zip(sources, ys):
        d.box(x, y, w, h, fc)
        d.text(x + w / 2, y + h * 0.62, title, size=11, weight="bold")
        d.text(x + w / 2, y + h * 0.24, sub, size=8.3, color=P["dim"])

    # 합성물 결과 박스
    rx, rw, rh = 66, 30, 40
    ry = (ys[0] + h + ys[-1]) / 2 - rh / 2
    d.box(rx, ry, rw, rh, P["chip"], ec=P["accent"], lw=1.8)
    d.text(rx + rw / 2, ry + rh * 0.62, "실제 기기\n시스템 이미지", size=12,
           weight="bold", color=P["accent"])
    d.text(rx + rw / 2, ry + rh * 0.28, "6개 레이어의\n합성물", size=9.5, color=P["dim"])

    for y in ys:
        d.arrow(x + w, y + h / 2, rx, ry + rh / 2, color=P["accent"],
                rad=0.05, lw=1.3)


diagram("01-code-origins", draw, w=11, h=8.5, xmax=100, ymax=90)

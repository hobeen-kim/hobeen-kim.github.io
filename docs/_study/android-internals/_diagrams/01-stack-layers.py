"""CH1 아키텍처 조감 — 안드로이드 소프트웨어 스택 레이어 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    layers = [
        ("Applications", "APK · 시스템 앱 · 서드파티 앱", P["blue"]),
        ("Java / System Framework", "system_server · Activity/PackageManager · services.jar", P["blue"]),
        ("ART 런타임", "DEX 실행 · AOT/JIT 컴파일 (구 Dalvik)", P["purple"]),
        ("JNI", "자바 ↔ 네이티브 경계", P["purple"]),
        ("Native 라이브러리 · 데몬", "SurfaceFlinger · media · libutils · vendor 데몬", P["green"]),
        ("Bionic", "libc · libm · linker (glibc 아님)", P["green"]),
        ("HAL", "Treble: HIDL/AIDL HAL · /vendor · VINTF", P["brown"]),
        ("Linux Kernel", "드라이버 · 스케줄러 · Androidism(Binder·ashmem·ION·lmk)", P["gray"]),
    ]

    x, w, h, gap = 22, 60, 9, 1.4
    top = 91
    ys = [top - i * (h + gap) for i in range(len(layers))]

    for (title, sub, fc), y in zip(layers, ys):
        d.box(x, y, w, h, fc)
        d.text(x + w / 2, y + h * 0.62, title, size=12, weight="bold")
        d.text(x + w / 2, y + h * 0.25, sub, size=8.8, color=P["dim"])

    # 유저스페이스 / 커널 구분 브래킷
    us_top = ys[0] + h
    us_bot = ys[6]
    d.box(x - 9, us_bot, 6, us_top - us_bot, P["chip"])
    d.text(x - 6, (us_top + us_bot) / 2, "유\n저\n스\n페\n이\n스", size=9, color=P["dim"])
    d.box(x - 9, ys[7], 6, h, P["chip"])
    d.text(x - 6, ys[7] + h / 2, "커\n널", size=9, color=P["dim"])

    # 인접 레이어 상호작용 화살표 (양방향 느낌)
    for i in range(len(layers) - 1):
        d.arrow(x + w + 2, ys[i] + h / 2, x + w + 2, ys[i + 1] + h / 2,
                color=P["accent"], style="<|-|>", lw=1.3)


diagram("01-stack-layers", draw, w=9.5, h=11, xmax=100, ymax=100)

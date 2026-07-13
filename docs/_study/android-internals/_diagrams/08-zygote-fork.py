"""CH8 Zygote fork 모델 — preload 후 COW로 앱 프로세스 분화 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # Zygote 본체
    d.box(4, 14, 30, 26, P["gray"], ec=P["accent"], lw=1.7)
    d.text(19, 37, "Zygote", size=12, weight="bold", color=P["accent"])
    d.text(19, 33.7, "app_process (32/64)", size=8.3, color=P["dim"])
    d.box(7, 26, 24, 5, P["blue"])
    d.text(19, 28.5, "preload 프레임워크 클래스", size=8.3)
    d.box(7, 20, 24, 5, P["green"])
    d.text(19, 22.5, "preload 리소스·JNI", size=8.3)
    d.box(7, 15, 24, 4, P["brown"])
    d.text(19, 17, "zygote 소켓 대기", size=8.3)

    # fork 대상들
    targets = [
        ("system_server", "부팅 직후 첫 fork", P["purple"], 34),
        ("앱 프로세스 A", "COW로 공유 페이지", P["blue"], 22),
        ("앱 프로세스 B", "필요 시에만 복제", P["green"], 10),
    ]
    for title, sub, fc, y in targets:
        d.box(66, y, 30, 9, fc)
        d.text(81, y + 5.6, title, size=10, weight="bold")
        d.text(81, y + 2.4, sub, size=8, color=P["dim"])
        d.arrow(34, 27, 66, y + 4.5, color=P["orange"], rad=0.04)

    d.text(50, 40, "fork() — 새 프로세스는 preload된 페이지를\nCOW(Copy-on-Write)로 공유",
           size=8.5, color=P["dim"])
    d.text(50, 5.5, "USAP 풀: 미리 fork해둔 예비 프로세스로 앱 시작 지연을 줄인다",
           size=8, color=P["dim"])


diagram("08-zygote-fork", draw, w=12, h=5.4, xmax=100, ymax=45)

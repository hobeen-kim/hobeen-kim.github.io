"""CH15 linker namespace — vendor 프로세스가 어떤 namespace로 라이브러리를 찾는가 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 프로세스 + 링커
    d.box(36, 42, 28, 6.5, P["gray"])
    d.text(50, 45.2, "vendor 프로세스 (dlopen/실행)", size=10)
    d.box(38, 32, 24, 6.5, P["blue"], ec=P["accent"], lw=1.8)
    d.text(50, 35.2, "linker64 (동적 링커)", size=10, weight="bold")

    # namespace 3종
    d.box(3, 10, 28, 15, P["blue"])
    d.text(17, 22, "default ns", size=10, weight="bold")
    d.text(17, 15.5, "/system/lib64\n/system_ext/lib64", size=9, color=P["dim"])

    d.box(36, 10, 28, 15, P["brown"])
    d.text(50, 22, "vndk ns", size=10, weight="bold")
    d.text(50, 15.5, "/apex/…/vndk/lib64\n(VNDK · LLNDK)", size=9, color=P["dim"])

    d.box(69, 10, 28, 15, P["green"])
    d.text(83, 22, "vendor/sphal ns", size=10, weight="bold")
    d.text(83, 15.5, "/vendor/lib64\n/odm/lib64", size=9, color=P["dim"])

    # 링커 → 각 namespace
    d.arrow(44, 32, 20, 25, color=P["accent"])
    d.arrow(50, 32, 50, 25, color=P["accent"])
    d.arrow(56, 32, 80, 25, color=P["accent"])

    # namespace 간 링크 (허용된 라이브러리만)
    d.arrow(69, 17.5, 64, 17.5, color=P["orange"], style="-|>")
    d.text(66.5, 19.6, "LLNDK만", size=8, color=P["orange"])
    d.text(6, 6.5, "ld.config.txt가 namespace별 search path와 링크 규칙을 정의한다",
           size=8.5, color=P["dim"], ha="left")


diagram("15-linker-namespaces", draw, w=13, h=5.4, xmax=100, ymax=50)

"""CH7 first-stage / second-stage init 분리 — ramdisk에서 실행 인계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # first-stage (ramdisk)
    d.box(4, 6, 40, 34, P["gray"], ec=P["accent"], lw=1.6)
    d.text(24, 37, "first-stage init", size=11, weight="bold", color=P["accent"])
    d.text(24, 33.5, "initramfs(ramdisk) 안 · 정적 링크", size=8.5, color=P["dim"])
    for i, s in enumerate([
        "/dev · /proc · /sys 마운트",
        "early property 초기화",
        "fstab 파싱 → /system·/vendor 마운트",
        "dm-verity(AVB) 설정",
        "SELinux 정책 로드 → enforcing",
        "setexeccon → second-stage exec",
    ]):
        d.box(7, 27.5 - i * 3.6, 34, 2.9, P["blue"])
        d.text(24, 27.5 - i * 3.6 + 1.45, s, size=8.4)

    # second-stage (system)
    d.box(56, 6, 40, 34, P["gray"])
    d.text(76, 37, "second-stage init", size=11, weight="bold")
    d.text(76, 33.5, "/system/bin/init 재실행 · 동적 링크", size=8.5, color=P["dim"])
    for i, s in enumerate([
        "property_service 시작",
        "ueventd(/dev 노드 생성)",
        "*.rc 파일 import·파싱",
        "on 트리거 액션 큐 실행",
        "service 정의대로 데몬 기동",
        "Zygote·핵심 데몬 start",
    ]):
        d.box(59, 27.5 - i * 3.6, 34, 2.9, P["green"])
        d.text(76, 27.5 - i * 3.6 + 1.45, s, size=8.4)

    d.arrow(44, 23, 56, 23, color=P["orange"], lw=2.0)
    d.text(50, 25.2, "execv", size=8.5, color=P["orange"])
    d.text(50, 20.6, "같은 PID 1\n유지", size=7.8, color=P["dim"])


diagram("07-first-second-init", draw, w=12, h=5.4, xmax=100, ymax=42)

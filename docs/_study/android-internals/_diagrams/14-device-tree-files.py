"""CH14 device 트리 — device/<vendor>/<board> 아래 핵심 파일과 역할 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 헤더: device 트리 루트
    d.box(5, 42, 42, 6, P["gray"], ec=P["accent"], lw=1.8)
    d.text(26, 45, "device/agmo/tractor/", size=11, weight="bold",
           color=P["accent"])

    rows = [
        ("AndroidProducts.mk", P["blue"],
         "제품 목록 등록 · lunch 타깃 노출"),
        ("tractor.mk", P["green"],
         "PRODUCT_PACKAGES · PRODUCT_COPY_FILES · inherit-product"),
        ("BoardConfig.mk", P["brown"],
         "파티션 크기 · 커널 · sepolicy 경로 · 아키텍처"),
        ("device.mk", P["purple"],
         "공통 device 설정 · init.rc 복사"),
        ("sepolicy/", P["chip"],
         "vendor SELinux 정책 (.te · file_contexts)"),
    ]

    x, w, h = 8, 26, 6
    ys = [34, 27, 20, 13, 6]
    for (name, fc, role), y in zip(rows, ys):
        d.box(x, y, w, h, fc)
        d.text(x + w / 2, y + h / 2, name, size=10)
        # 트리 연결선 느낌의 화살표
        d.arrow(x + w, y + h / 2, 40, y + h / 2, color=P["dim"], lw=1.2)
        d.text(41, y + h / 2, role, size=8.5, color=P["dim"], ha="left")


diagram("14-device-tree-files", draw, w=13, h=5.6, xmax=100, ymax=50)

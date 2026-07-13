"""CH5 vold 이벤트 흐름 — 커널 uevent에서 앱의 /storage 뷰까지."""
from _common import diagram


def draw(d):
    P = d.P

    nodes = [
        (4, 30, 18, 8, "커널\n(uevent / netlink)", P["gray"]),
        (30, 30, 18, 8, "vold\n(볼륨 매니저)", P["blue"]),
        (56, 38, 18, 8, "StorageManager\nService", P["green"]),
        (56, 26, 18, 8, "FUSE 데몬\n(sdcard / MediaProvider)", P["brown"]),
        (82, 30, 15, 8, "앱의\n/storage 뷰", P["purple"]),
    ]
    for x, y, w, h, label, fc in nodes:
        d.box(x, y, w, h, fc)
        d.text(x + w / 2, y + h / 2, label, size=9)

    d.arrow(22, 34, 30, 34)
    d.text(26, 35.6, "SD 삽입", size=8, color=P["dim"])
    d.arrow(48, 35, 56, 41, color=P["orange"])
    d.text(52, 39.5, "Binder 콜백", size=8, color=P["orange"])
    d.arrow(48, 33, 56, 30, color=P["violet"])
    d.text(52, 28.5, "mount 지시", size=8, color=P["violet"])
    d.arrow(74, 30, 82, 33)
    d.text(78, 31.6, "권한별 뷰", size=8, color=P["dim"])

    # storaged / storagestats 보조
    d.box(30, 14, 44, 8, P["chip"])
    d.text(52, 18, "storaged · storagestats — I/O 통계 / per-uid 사용량 집계",
           size=9, color=P["dim"])
    d.arrow(39, 30, 39, 22, color=P["edge"], lw=1.1, ls="--")


diagram("05-vold-flow", draw, w=12, h=5.4, ymax=48)

"""CH9 system_server 기동과 서비스 그룹 — Zygote fork 후 3단계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 기동 흐름
    d.box(3, 34, 20, 9, P["purple"])
    d.text(13, 40.3, "Zygote", size=10, weight="bold")
    d.text(13, 36.7, "fork()", size=8.3, color=P["dim"])
    d.box(3, 20, 20, 9, P["gray"], ec=P["accent"], lw=1.6)
    d.text(13, 26.3, "SystemServer", size=10, weight="bold", color=P["accent"])
    d.text(13, 22.7, ".main()", size=8.3, color=P["dim"])
    d.arrow(13, 34, 13, 29, color=P["accent"])

    groups = [
        ("startBootstrapServices", P["blue"],
         "AMS · PMS · PowerMS\nLightsService · Installer", 32),
        ("startCoreServices", P["brown"],
         "BatteryService · UsageStats\nWebViewUpdate", 32 - 0),
        ("startOtherServices", P["green"],
         "WMS · InputMS · NetworkMS\nAudio · Bluetooth 등 다수", 32),
    ]
    ys = [30, 18, 6]
    for (title, fc, sub, x), y in zip(groups, ys):
        d.box(32, y, 40, 10.5, fc)
        d.text(52, y + 7.6, title + "()", size=10, weight="bold")
        d.text(52, y + 3.4, sub, size=8.2, color=P["dim"])
        d.arrow(23, 24.5, 32, y + 5.25, color=P["accent"], rad=0.05)

    # watchdog
    d.box(80, 18, 17, 11, P["chip"], ec=P["orange"], lw=1.5)
    d.text(88.5, 25, "Watchdog", size=10, weight="bold", color=P["orange"])
    d.text(88.5, 21, "블로킹 감시\n→ 강제 재시작", size=8, color=P["dim"])
    d.arrow(72, 23, 80, 23, color=P["orange"])

    d.text(52, 1.5, "세 단계를 마치면 SystemServer가 메인 루퍼로 진입해 서비스들을 서비스한다",
           size=8, color=P["dim"])


diagram("09-system-server", draw, w=12.5, h=5.6, xmax=100, ymax=45)

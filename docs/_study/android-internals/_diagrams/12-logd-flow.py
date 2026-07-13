"""CH12 logd 흐름 — 생산자에서 버퍼, 리더까지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 생산자 (왼쪽)
    producers = [
        ("앱 / 프레임워크", "Log.d(), liblog"),
        ("네이티브 데몬", "__android_log_print"),
        ("커널 (선택)", "logd → kmsg 브릿지"),
    ]
    for i, (t, s) in enumerate(producers):
        y = 34 - i * 11
        d.box(3, y, 22, 8, P["blue"])
        d.text(14, y + 5, t, size=9, weight="bold")
        d.text(14, y + 2, s, size=7.8, color=P["dim"])
        d.arrow(25, y + 4, 33, 24, color=P["accent"], lw=1.2, rad=0.05)

    d.text(29, 12, "/dev/socket/logdw\n(유닉스 소켓)", size=8, color=P["dim"])

    # logd 프로세스 + 버퍼들 (가운데)
    d.box(33, 6, 34, 36, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 39, "logd (링 버퍼, 메모리)", size=10, weight="bold", color=P["accent"])
    buffers = ["main", "system", "radio", "events", "crash"]
    for i, b in enumerate(buffers):
        y = 32 - i * 5.6
        d.box(37, y, 26, 4.6, P["chip"])
        d.text(50, y + 2.3, b, size=9)

    # 리더 (오른쪽)
    d.box(74, 24, 24, 12, P["green"])
    d.text(86, 32, "logcat", size=10, weight="bold")
    d.text(86, 27.5, "-b <buffer> -v <fmt>\n--pid / tag 필터", size=8, color=P["dim"])
    d.arrow(67, 30, 74, 30, color=P["accent"], lw=1.4)
    d.text(70.5, 32, "/logdr", size=7.5, color=P["dim"])

    d.box(74, 8, 24, 11, P["purple"])
    d.text(86, 15.5, "구독자", size=10, weight="bold")
    d.text(86, 11.5, "DropBox · statsd\n· incidentd", size=8, color=P["dim"])
    d.arrow(67, 16, 74, 14, color=P["orange"], lw=1.3, rad=-0.05)


diagram("12-logd-flow", draw, w=12, h=6, ymax=46)

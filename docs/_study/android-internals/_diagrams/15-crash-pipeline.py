"""CH15 크래시 파이프라인 — 시그널부터 tombstone까지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("크래시 프로세스", "SIGSEGV / SIGABRT\n수신", P["blue"]),
        ("libc 시그널 핸들러", "debuggerd_signal\n파이프 생성", P["green"]),
        ("crash_dump", "ptrace 부착\n스레드 정지·언와인드", P["brown"]),
        ("tombstoned", "tombstone 슬롯\n관리·기록", P["purple"]),
    ]

    x, w, h, gap = 2, 21, 16, 3.5
    y = 26
    xs = [x + i * (w + gap) for i in range(len(stages))]
    for i, ((title, sub, fc), xi) in enumerate(zip(stages, xs)):
        d.box(xi, y, w, h, fc, ec=P["accent"] if i == 0 else None,
              lw=1.8 if i == 0 else 1.4)
        d.text(xi + w / 2, y + h * 0.68, title, size=10, weight="bold")
        d.text(xi + w / 2, y + h * 0.28, sub, size=8.3, color=P["dim"])
        if i < len(stages) - 1:
            d.arrow(xi + w, y + h / 2, xs[i + 1], y + h / 2, color=P["accent"])

    # 산출물
    last = xs[-1]
    d.box(last - 4, 6, 25, 12, P["chip"])
    d.text(last + 8.5, 14, "/data/tombstones/\ntombstone_NN", size=9)
    d.text(last + 8.5, 9, "logcat (F DEBUG)", size=9, color=P["dim"])
    d.arrow(last + w / 2, y, last + 8.5, 18, color=P["orange"])

    d.text(2, 2.5, "ndk-stack · llvm-symbolizer로 backtrace를 심볼화한다",
           size=8.5, color=P["dim"], ha="left")


diagram("15-crash-pipeline", draw, w=13, h=5, xmax=100, ymax=44)

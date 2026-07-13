"""CH12 크래시 수집 경로 — 시그널에서 tombstone·DropBox까지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 네이티브 크래시 경로 (위쪽 행)
    d.box(2, 30, 20, 9, P["blue"])
    d.text(12, 34.5, "네이티브 프로세스\nSIGSEGV/SIGABRT", size=8.8, weight="bold")

    d.box(28, 30, 20, 9, P["brown"])
    d.text(38, 34.5, "debuggerd\n시그널 핸들러", size=9, weight="bold")

    d.box(54, 30, 20, 9, P["purple"])
    d.text(64, 34.5, "crash_dump\n(ptrace 언와인드)", size=8.8, weight="bold")

    d.box(80, 30, 18, 9, P["green"])
    d.text(89, 34.5, "tombstone\n/data/tombstones", size=8.5, weight="bold")

    d.arrow(22, 34.5, 28, 34.5, color=P["accent"], lw=1.4)
    d.arrow(48, 34.5, 54, 34.5, color=P["accent"], lw=1.4)
    d.arrow(74, 34.5, 80, 34.5, color=P["accent"], lw=1.4)

    # 자바 ANR/크래시 경로 (아래 행)
    d.box(2, 14, 20, 9, P["blue"])
    d.text(12, 18.5, "앱 프로세스\nANR · 미처리 예외", size=8.8, weight="bold")

    d.box(28, 14, 20, 9, P["brown"])
    d.text(38, 18.5, "system_server\nAMS 감지", size=9, weight="bold")

    d.box(54, 14, 20, 9, P["purple"])
    d.text(64, 18.5, "ANR dump\n(traces.txt)", size=8.8, weight="bold")

    d.arrow(22, 18.5, 28, 18.5, color=P["accent"], lw=1.4)
    d.arrow(48, 18.5, 54, 18.5, color=P["accent"], lw=1.4)

    # 공통 수집소 DropBox
    d.box(78, 12, 20, 11, P["gray"], ec=P["accent"], lw=1.6)
    d.text(88, 19.5, "DropBoxManager", size=9.5, weight="bold", color=P["accent"])
    d.text(88, 15, "/data/system/dropbox\nbugreport로 회수", size=8, color=P["dim"])
    d.arrow(74, 18.5, 78, 18, color=P["orange"], lw=1.3)
    d.arrow(89, 30, 89, 23, color=P["orange"], lw=1.3)

    d.text(50, 5, "tombstone·traces 모두 DropBox에 사본 적재 → bugreport·adb pull로 수집",
           size=8.5, color=P["dim"])


diagram("12-crash-flow", draw, w=12, h=5.6, ymax=42)

"""CH26 eBPF 무계측 프로파일링 — 노드 단위 수집 (light/dark PNG)."""
from _common import diagram
from _common import Line2D


def draw(d):
    P = d.P

    # 쿠버네티스 노드
    d.box(4, 10, 70, 40, P["gray"], ec=P["edge"], lw=1.5)
    d.text(9, 47, "쿠버네티스 노드", size=11, weight="bold", ha="left")

    procs = [
        (16, "Go 서비스", P["blue"], "애플리케이션"),
        (32, "Java 서비스", P["brown"], "애플리케이션"),
        (48, "Python 서비스", P["green"], "애플리케이션"),
        (65, "서드파티 바이너리", P["purple"], "소스 없음"),
    ]
    for x, t, c, sub in procs:
        d.box(x - 7.5, 40, 15, 6, c)
        d.text(x, 43.6, t, size=9, weight="bold")
        d.text(x, 41.4, sub, size=7.5, color=P["dim"])

    # 커널 공간
    d.box(9, 27, 60, 7.5, P["brown"], ec=P["orange"], lw=1.5)
    d.text(14, 32.8, "커널 공간", size=10, weight="bold", ha="left", color=P["orange"])
    d.box(28, 28, 22, 4.4, P["chip"])
    d.text(39, 30.2, "eBPF 프로그램 (perf_event 샘플러)", size=8.5)

    # 프로세스 → eBPF
    for x, t, c, sub in procs:
        d.arrow(x, 40, 39, 34.5, color=P["violet"], lw=1.5, ls=(0, (4, 3)))

    # Alloy
    d.box(24, 15, 30, 7, P["green"], ec=P["accent"], lw=1.8)
    d.text(39, 20, "Alloy", size=12, weight="bold", color=P["accent"])
    d.text(39, 17, "pyroscope.ebpf · DaemonSet", size=8.5, color=P["dim"])

    d.arrow(39, 27, 39, 22, color=P["orange"], lw=2.2)
    d.text(43.5, 24.5, "eBPF 이벤트", size=8, color=P["orange"], ha="left")

    # Pyroscope (노드 밖)
    d.box(80, 24, 17, 13, P["gray"], ec=P["accent"], lw=1.9)
    d.text(88.5, 32, "Pyroscope", size=12, weight="bold", color=P["accent"])
    d.text(88.5, 28, "노드별 결과\n중앙 집계", size=8.5, color=P["dim"])

    d.arrow(54, 18.5, 88.5, 24, color=P["orange"], lw=2.2)
    d.text(72, 23.5, "push", size=8.5, color=P["orange"])

    leg = [
        Line2D([0], [0], color=P["violet"], lw=2.2, ls="--",
               label="프로세스 → 커널 스택 캡처"),
        Line2D([0], [0], color=P["orange"], lw=2.2,
               label="eBPF 이벤트 → Alloy → Pyroscope"),
    ]
    d.legend(leg, anchor=(0.005, 0.02))


diagram("26-ebpf-node", draw, w=13, h=6.5, ymax=52)

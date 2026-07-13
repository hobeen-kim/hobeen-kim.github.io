"""CH3 리눅스 pseudo-filesystem — 종류·마운트 지점·안드로이드 용도 매핑."""
from _common import diagram


def draw(d):
    P = d.P

    rows = [
        ("procfs", "/proc", "프로세스·커널 상태", P["blue"]),
        ("sysfs", "/sys", "디바이스·드라이버 트리", P["blue"]),
        ("cgroupfs", "/sys/fs/cgroup", "앱 그룹 CPU·메모리 제어", P["green"]),
        ("tracefs", "/sys/kernel/tracing", "ftrace·atrace 커널 트레이싱", P["green"]),
        ("debugfs", "/sys/kernel/debug", "디버그 노출(유저빌드 비활성)", P["gray"]),
        ("configfs", "/config", "USB gadget·기능 구성", P["purple"]),
        ("functionfs", "/dev/usb-ffs/adb", "adbd USB 엔드포인트", P["purple"]),
        ("bpf", "/sys/fs/bpf", "eBPF 맵·트래픽 통계", P["brown"]),
        ("pstore", "/sys/fs/pstore", "커널 패닉 로그 보존", P["brown"]),
        ("tmpfs", "/dev, /mnt", "RAM 기반 임시 노드", P["chip"]),
        ("overlayfs", "system 위 레이어", "adb remount RW 오버레이", P["chip"]),
        ("FUSE / sdcardfs", "/storage/emulated", "외부 스토리지 에뮬레이션", P["chip"]),
        ("incremental-fs", "/data/incremental", "Play 스트리밍 설치", P["chip"]),
    ]

    n = len(rows)
    top = 46.0
    row_h = 3.6
    for i, (fs, mount, use, fc) in enumerate(rows):
        y = top - i * row_h
        d.box(4, y, 20, row_h - 0.6, fc)
        d.text(14, y + (row_h - 0.6) / 2, fs, size=9, weight="bold")
        d.box(26, y, 26, row_h - 0.6, P["chip"])
        d.text(39, y + (row_h - 0.6) / 2, mount, size=8.5, color=P["dim"])
        d.arrow(24, y + (row_h - 0.6) / 2, 26, y + (row_h - 0.6) / 2,
                color=P["edge"], lw=1.2)
        d.text(55, y + (row_h - 0.6) / 2, use, size=8.5, ha="left")


diagram("03-pseudo-fs", draw, w=11, h=7.2, ymax=50)

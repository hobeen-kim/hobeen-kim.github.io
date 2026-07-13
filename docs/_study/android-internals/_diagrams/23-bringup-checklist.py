"""CH23 기동 실패 진단 플로 — 증상별 체크 순서 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    steps = [
        ("ps -A | grep agcand", "프로세스가 떠 있나?", P["blue"], 40),
        ("logcat / dmesg", "rc 로드 · seclabel 확인", P["green"], 31),
        ("dmesg | grep avc", "SELinux denial 있나?", P["purple"], 22),
        ("service list / find", "servicemanager에 등록됐나?", P["brown"], 13),
        ("service call ...", "트랜잭션 응답 오나?", P["blue"], 4),
    ]
    for cmd, q, fc, y in steps:
        d.box(6, y, 34, 6.5, fc)
        d.text(23, y + 4.3, cmd, size=8.5, weight="bold")
        d.text(23, y + 1.6, q, size=7.8, color=P["dim"])

    # 아래로 흐름 화살표
    for y in (40, 31, 22, 13):
        d.arrow(23, y, 23, y - 2.5, color=P["orange"])

    # 실패 분기 라벨 (오른쪽)
    causes = [
        ("→ rc 미로드 · seclabel 누락", 43),
        ("→ NET_RAW capability 누락", 34),
        ("→ agcand.te allow 추가", 25),
        ("→ service_contexts · VINTF 불일치", 16),
        ("→ 라이브러리 namespace 로드 실패", 7),
    ]
    for text, y in causes:
        d.text(46, y, text, size=8, ha="left", color=P["violet"])

    d.text(70, 24, "각 단계에서 막히면\n오른쪽 원인부터 점검",
           size=8.5, color=P["dim"])


diagram("23-bringup-checklist", draw, w=13, h=6.4, xmax=100, ymax=49)

"""CH12 §4 캐스케이딩 SFU — 리전 간 릴레이로 스트림당 1벌만 넘긴다 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 룸 배치 디렉터리
    d.box(40, 40.5, 20, 5.5, P["brown"])
    d.text(50, 43.25, "룸 배치 디렉터리\n(Redis 등)", size=8.5)

    # 서울 리전
    d.box(2, 3, 42, 34, P["gray"])
    d.text(4, 34.6, "서울 리전", size=10, weight="bold", ha="left")
    for (y, lbl) in [(24, "카메라 A\n(농기계)"), (15, "카메라 B\n(농기계)")]:
        d.box(5, y, 15, 6.4, P["blue"])
        d.text(12.5, y + 3.2, lbl, size=8.8)
    d.box(5, 5.5, 15, 6.4, P["chip"])
    d.text(12.5, 8.7, "운영자\n(국내)", size=8.8)
    d.box(27, 12, 13, 12, P["purple"], ec=P["accent"], lw=1.6)
    d.text(33.5, 18, "SFU-1", size=10, weight="bold")
    d.arrow(20, 27.2, 27, 21.5, color=P["accent"])
    d.arrow(20, 18.2, 27, 18.2, color=P["accent"])
    d.arrow(27, 14.5, 20, 9.5, color=P["orange"])

    # 버지니아 리전
    d.box(56, 3, 42, 34, P["gray"])
    d.text(96, 34.6, "버지니아 리전", size=10, weight="bold", ha="right")
    d.box(60, 12, 13, 12, P["purple"], ec=P["accent"], lw=1.6)
    d.text(66.5, 18, "SFU-2", size=10, weight="bold")
    for i, y in enumerate([24, 15, 6]):
        d.box(80, y, 15, 6.4, P["chip"])
        d.text(87.5, y + 3.2, f"운영자 {i + 1}\n(해외)", size=8.8)
        d.arrow(73, 18, 80, y + 3.2, color=P["orange"])

    # 릴레이
    d.arrow(40, 20.5, 60, 20.5, color=P["accent"], lw=2.4)
    d.text(50, 23.4, "릴레이\n(스트림당 1벌)", size=8.5, color=P["accent"], weight="bold")
    d.arrow(60, 15.5, 40, 15.5, color=P["dim"], lw=1.3, ls="--")
    d.text(50, 13.2, "PLI·RTCP 피드백", size=8, color=P["dim"])

    # 디렉터리 조회
    d.arrow(43, 40.5, 35, 24, color=P["violet"], lw=1.2, ls="--", style="-")
    d.arrow(57, 40.5, 65, 24, color=P["violet"], lw=1.2, ls="--", style="-")


diagram("12-cascading", draw, w=13, h=6.2, ymax=47)

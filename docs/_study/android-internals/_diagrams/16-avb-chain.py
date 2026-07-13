"""CH16 AVB 신뢰 체인 — 부트로더에서 vbmeta를 거쳐 각 파티션 해시로 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 루트 오브 트러스트
    d.box(30, 40, 40, 7, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 43.5, "락된 부트로더 (공개키 내장 · ROT)", size=10, weight="bold")

    # vbmeta
    d.box(30, 27, 40, 8, P["purple"])
    d.text(50, 31, "vbmeta (서명됨)\nrollback index · 디스크립터", size=9.5)

    # 파티션 디스크립터
    d.box(5, 8, 26, 11, P["blue"])
    d.text(18, 14.5, "boot.img", size=10, weight="bold")
    d.text(18, 10.5, "hash 디스크립터", size=8.5, color=P["dim"])

    d.box(37, 8, 26, 11, P["green"])
    d.text(50, 14.5, "system", size=10, weight="bold")
    d.text(50, 10.5, "hashtree (dm-verity)", size=8.5, color=P["dim"])

    d.box(69, 8, 26, 11, P["brown"])
    d.text(82, 14.5, "vendor", size=10, weight="bold")
    d.text(82, 10.5, "hashtree (dm-verity)", size=8.5, color=P["dim"])

    # 화살표
    d.arrow(50, 40, 50, 35, color=P["accent"])
    d.text(52, 37.5, "서명 검증", size=8, color=P["orange"], ha="left")
    d.arrow(44, 27, 20, 19, color=P["accent"])
    d.arrow(50, 27, 50, 19, color=P["accent"])
    d.arrow(56, 27, 80, 19, color=P["accent"])
    d.text(30, 22.5, "해시 검증", size=8, color=P["orange"])


diagram("16-avb-chain", draw, w=13, h=5, xmax=100, ymax=48)

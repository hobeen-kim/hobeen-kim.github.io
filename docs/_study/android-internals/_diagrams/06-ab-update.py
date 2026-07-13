"""CH6 A/B 무중단 업데이트 — update_engine가 비활성 슬롯에 적용하고 슬롯을 전환."""
from _common import diagram


def draw(d):
    P = d.P

    # 현재 상태
    d.box(4, 30, 20, 10, P["green"])
    d.text(14, 37, "슬롯 A (활성)", size=9, weight="bold", color=P["accent"])
    d.text(14, 33, "현재 부팅 중\n사용자 사용", size=8, color=P["dim"])

    d.box(4, 14, 20, 10, P["gray"])
    d.text(14, 21, "슬롯 B (비활성)", size=9, weight="bold")
    d.text(14, 17, "구버전 / 빈 슬롯", size=8, color=P["dim"])

    # update_engine 적용
    d.box(34, 22, 26, 12, P["blue"])
    d.text(47, 30.5, "update_engine", size=10, weight="bold", color=P["accent"])
    d.text(47, 26, "payload.bin 스트리밍\n백그라운드 블록 적용\nVirtual A/B: 스냅샷", size=8,
           color=P["dim"])
    d.arrow(24, 19, 34, 25, color=P["orange"])
    d.text(29, 23.5, "쓰기", size=8, color=P["orange"])

    # 전환
    d.box(70, 22, 26, 12, P["purple"])
    d.text(83, 30.5, "슬롯 전환 + 재부팅", size=9.5, weight="bold",
           color=P["accent"])
    d.text(83, 26, "bootctl set-active B\n실패 시 A로 롤백", size=8, color=P["dim"])
    d.arrow(60, 28, 70, 28, color=P["violet"])

    d.text(50, 8, "핵심: 실행 중 슬롯을 건드리지 않으므로 다운타임 0 — 재부팅 한 번으로 완료",
           size=8.5, color=P["dim"], ha="center", style="italic")


diagram("06-ab-update", draw, w=12, h=4.8, ymax=44)

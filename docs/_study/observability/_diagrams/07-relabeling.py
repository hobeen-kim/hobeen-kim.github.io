"""CH07 §4 Relabeling 파이프라인 — 스크레이프 전 타깃 필터링·재작성 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 파이프라인 행
    d.box(2, 37, 16, 10, P["gray"])
    d.text(10, 42, "SD가 만든 타깃\n+ __meta_* 라벨", size=9)

    for i, label in enumerate(["relabel #1", "relabel #2", "relabel #N"]):
        x = 22 + i * 18
        d.box(x, 38, 14, 8, P["blue"])
        d.text(x + 7, 43, label, size=9.5, weight="bold")
        d.text(x + 7, 40, "source→regex→action", size=7, color=P["dim"])

    d.box(78, 37, 18, 10, P["green"], ec=P["accent"], lw=1.8)
    d.text(87, 42, "최종 타깃\n__address__ 확정", size=9, color=P["accent"])

    for x1, x2 in [(18, 22), (36, 40), (54, 58), (72, 78)]:
        d.arrow(x1, 42, x2, 42, color=P["accent"])

    # 스크레이프 실행 (최종 아래)
    d.box(78, 25, 18, 7, P["chip"], ec=P["orange"], lw=1.4)
    d.text(87, 28.5, "스크레이프 실행\nkeep된 타깃만 GET", size=9, color=P["orange"])
    d.arrow(87, 37, 87, 32, color=P["orange"])
    d.text(70, 30, "drop된 타깃은\n여기서 제외", size=8, color=P["orange"], ha="right")

    # 하단 왼쪽: action 종류
    d.box(3, 3, 53, 18, P["chip"])
    d.text(29.5, 18.4, "relabel action", size=9.5, weight="bold", color=P["accent"])
    actions = [
        ("keep / drop", "매치 타깃 유지 / 제거"),
        ("replace", "결과를 target_label에 기록 (기본)"),
        ("labelmap", "소스 라벨명을 새 이름으로 복사"),
        ("labeldrop / labelkeep", "라벨 이름 기준 제거 / 유지"),
        ("hashmod", "해시 기반 샤딩"),
    ]
    for i, (a, desc) in enumerate(actions):
        yy = 14.8 - i * 2.6
        d.text(6, yy, a, size=8.3, color=P["orange"], ha="left", weight="bold")
        d.text(24, yy, desc, size=8, color=P["dim"], ha="left")

    # 하단 오른쪽: 핵심 원리
    d.box(60, 3, 36, 18, P["purple"])
    d.text(78, 18.4, "핵심 원리", size=9.5, weight="bold")
    d.text(78, 12.5, "__ 로 시작하는 라벨은\nrelabel 단계에서만 보이고 사라진다",
           size=8.5)
    d.text(78, 6.5, "target_label로 명시 승격해야\n영구 라벨로 남는다", size=8.5,
           color=P["accent"], weight="bold")


diagram("07-relabeling", draw, w=13, h=6.6, ymax=48)

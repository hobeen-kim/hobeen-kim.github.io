"""CH18 §7 태스크 상태(TaskStatus 1~6)와 전이 (light/dark PNG)."""
from _common import diagram

W, H = 22, 9


def node(d, x, y, title, sub, color):
    d.box(x, y, W, H, d.P[color])
    d.text(x + W / 2, y + H / 2 + 1.6, title, size=11.5, weight="bold")
    d.text(x + W / 2, y + H / 2 - 1.7, sub, size=8.5)


def draw(d):
    P = d.P
    node(d, 4, 38, "Template (5)", "v4 도입", "purple")
    node(d, 4, 20, "Planned (1)", "FMIS 또는 MICS가 준비", "gray")
    node(d, 40, 20, "Running (2)", "TC당 동시에 1개", "green")
    node(d, 76, 20, "Paused (3)", "미완료 · TC 쪽 최종 상태 가능", "brown")
    node(d, 58, 2, "Completed (4)", "오퍼레이터만 설정 · 선택 지원", "blue")
    node(d, 4, 2, "Canceled (6)", "v4 도입", "purple")

    d.arrow(26, 24.5, 40, 24.5)
    d.text(33, 26.4, "시작", size=9.5, color=P["accent"])

    d.arrow(62, 26.5, 76, 26.5)
    d.text(69, 28.4, "일시정지", size=9.5, color=P["accent"])
    d.arrow(76, 22.5, 62, 22.5)
    d.text(69, 20.4, "재개", size=9.5, color=P["accent"])

    d.arrow(26, 42.5, 46, 29.2, color=P["violet"], ls="--")
    d.text(42, 39.2, "시작하면 복사본이\n새 태스크로 실행", size=9, color=P["violet"])

    d.arrow(51, 20, 63, 11.2)
    d.text(51.5, 14.2, "완료", size=9.5, color=P["accent"])
    d.arrow(87, 20, 75, 11.2)
    d.text(86.5, 14.2, "완료", size=9.5, color=P["accent"])

    d.arrow(15, 20, 15, 11.2, color=P["orange"], ls="--")
    d.text(24.5, 15.6, "철회 신호\n(FMIS·MICS 양방향)", size=9, color=P["orange"])


diagram("18-task-state-machine", draw, w=12, h=6, xmax=100, ymax=50)

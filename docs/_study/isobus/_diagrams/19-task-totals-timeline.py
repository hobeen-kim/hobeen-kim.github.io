"""CH19 §12 task total 처리 타임라인 — 시작·재개, 측정, 주기 수집, 일시정지 (light/dark PNG)."""
from _common import diagram

TC_X, CL_X = 34, 84
TOP = 57
STEP = 3.55

# (종류, 내용) — "tc": TC->클라이언트, "cl": 클라이언트->TC, "note_cl"/"note_tc": 생명선 위 메모
ROWS = [
    ("tc", "TC Status (E)   totals active 0 -> 1"),
    ("note_cl", "task total = 0, 카운트 시작"),
    ("tc", "Value command (3)   저장해 둔 task total 복원 (재개일 때)"),
    ("tc", "Measurement (4~8)   예: time interval"),
    ("cl", "PDACK (D)   오류 코드 0"),
    ("cl", "Value command (3)   측정 시작 시점의 값"),
    ("cl", "Value command (3)   트리거마다 반복"),
    ("tc", "Request value (2)   task total, 예: 1분마다"),
    ("cl", "Value command (3)   현재 total"),
    ("tc", "TC Status (E)   totals active 1 -> 0"),
    ("note_cl", "measurement 모두 중지, total 정지"),
    ("tc", "Request value (2)   최종 task total"),
    ("cl", "Value command (3)   최종 값"),
    ("note_tc", "Time 요소에 저장"),
]

PHASES = [
    (0, 2, "시작·재개"),
    (3, 6, "측정 설정"),
    (7, 8, "주기 수집"),
    (9, 13, "일시정지·완료"),
]


def row_y(i):
    return TOP - 4.6 - i * STEP


def lifeline_segments(note_kind):
    gaps = [row_y(i) for i, (k, _) in enumerate(ROWS) if k == note_kind]
    top, bottom = TOP - 2.7, row_y(len(ROWS) - 1) - 1.6
    segs, start = [], top
    for g in gaps:
        segs.append((start, g + 1.35))
        start = g - 1.35
    segs.append((start, bottom))
    return [(a, b) for a, b in segs if a - b > 0.5]


def draw(d):
    P = d.P
    for x, name, note_kind in ((TC_X, "TC 서버", "note_tc"),
                               (CL_X, "TC 클라이언트 (작업기)", "note_cl")):
        d.box(x - 9, TOP - 2.6, 18, 3.4, P["blue"])
        d.text(x, TOP - 0.9, name, size=10, weight="bold")
        for y1, y2 in lifeline_segments(note_kind):
            d.arrow(x, y1, x, y2, color=P["edge"], lw=1.1, style="-", ls="--")

    for i, (kind, label) in enumerate(ROWS):
        y = row_y(i)
        if kind == "tc":
            d.arrow(TC_X, y, CL_X, y, color=P["accent"])
            d.text((TC_X + CL_X) / 2, y + 0.95, label, size=8.3)
        elif kind == "cl":
            d.arrow(CL_X, y, TC_X, y, color=P["orange"], ls="--")
            d.text((TC_X + CL_X) / 2, y + 0.95, label, size=8.3)
        else:
            x = CL_X if kind == "note_cl" else TC_X
            d.box(x - 10.5, y - 1.2, 21, 2.4, P["green"])
            d.text(x, y, label, size=8.3)

    for first, last, name in PHASES:
        y1 = row_y(first) + 1.8
        y2 = row_y(last) - 1.0
        d.box(1.5, y2, 14, y1 - y2, P["gray"], lw=1.0)
        d.text(8.5, (y1 + y2) / 2, name, size=9, weight="bold", color=P["dim"])


diagram("19-task-totals-timeline", draw, w=12, h=7.6, xmax=100, ymax=58)

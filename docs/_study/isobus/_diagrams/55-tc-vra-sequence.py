"""CH55 §4 처방 맵 기반 가변 살포 시나리오 시퀀스 (light/dark PNG)."""
from _common import diagram

LANES = {
    "FMIS": (9, "FMIS", "(농장 관리 소프트웨어)"),
    "FS": (26, "File Server", "(ISO 11783-13)"),
    "TC": (45, "Task Controller", "(ISO 11783-10)"),
    "GPS": (62, "GPS 수신기", ""),
    "SC": (77.5, "Section Control", "(작업기 ECU)"),
    "LOG": (92.5, "As-Applied 로그", ""),
}

# ("phase", text) | (src, dst, label, dashed)
STEPS = [
    ("phase", "1. 작업 준비"),
    ("FMIS", "FS", "처방 맵 파일 업로드\n(prescription_map.xml)", False),
    ("FS", "FMIS", "업로드 완료", True),
    ("TC", "FS", "처방 맵 파일 다운로드 요청", False),
    ("FS", "TC", "처방 맵 파일 전달", True),
    ("TC", "TC", "처방 맵 파싱 및\n격자 셀별 목표값 로드", False),
    ("phase", "2. 작업 시작"),
    ("FMIS", "TC", "Task Start 명령", False),
    ("TC", "FMIS", "Task Start 확인", True),
    ("phase", "3. 실시간 살포 (작업 중 1초 간격으로 반복)"),
    ("GPS", "TC", "NMEA 2000 GNSS Position Data\n(PGN 129029) 현재 위치 (lat, lon)", False),
    ("TC", "TC", "위치 → 처방 맵 격자 셀 조회\n목표 살포량 결정", False),
    ("TC", "SC", "Section Control 명령\n(섹션 ON/OFF 비트맵)", False),
    ("TC", "SC", "Rate Control 명령\n(목표 살포량 L/ha)", False),
    ("SC", "TC", "실제 살포량 피드백", True),
    ("TC", "LOG", "As-Applied 레코드 저장\n(위치, 목표값, 실제값, 시간)", False),
    ("phase", "4. 작업 종료 및 데이터 회수"),
    ("FMIS", "TC", "Task Stop 명령", False),
    ("TC", "FMIS", "Task Stop 확인", True),
    ("TC", "FS", "As-Applied 로그 파일 업로드\n(task_log_20260413.xml)", False),
    ("FS", "TC", "업로드 완료", True),
    ("FMIS", "FS", "로그 파일 다운로드", False),
    ("FS", "FMIS", "로그 파일 전달", True),
    ("FMIS", "FMIS", "As-Applied Map\n생성 및 분석", False),
]


def label(d, x, y, s, ha="center"):
    d.ax.text(x, y, s, fontsize=8, color=d.P["text"], ha=ha, va="center", zorder=6,
              linespacing=1.15,
              bbox=dict(facecolor=d.P["bg"], edgecolor="none", pad=0.6, alpha=0.92))


def draw(d):
    P = d.P
    top = 129.0
    for key, (x, name, sub) in LANES.items():
        d.box(x - 6.8, top, 13.6, 7.0, P["blue"])
        d.text(x, top + (4.6 if sub else 3.5), name, size=9, weight="bold")
        if sub:
            d.text(x, top + 1.9, sub, size=7.5, color=P["dim"])
        d.ax.plot([x, x], [3.0, top], color=P["edge"], lw=1.0, ls=(0, (3, 3)), zorder=1)

    y = top - 4.0
    loop_top = None
    for step in STEPS:
        if step[0] == "phase":
            if loop_top is not None:
                d.box(38.5, y + 1.2, 60.5, loop_top - y - 1.6, "none", ec=P["orange"], lw=1.0)
                loop_top = None
            d.box(1, y - 1.8, 98, 3.6, P["gray"], ec=P["gray"])
            d.text(2.2, y, step[1], size=9, weight="bold", ha="left", color=P["accent"])
            if step[1].startswith("3."):
                loop_top = y - 2.3
            y -= 6.6
            continue
        src, dst, text, dashed = step
        xs, xd = LANES[src][0], LANES[dst][0]
        two = "\n" in text
        if src == dst:
            d.ax.plot([xs, xs + 3.5, xs + 3.5], [y + 1.0, y + 1.0, y - 1.0], color=P["accent"], lw=1.4, zorder=4)
            d.arrow(xs + 3.5, y - 1.0, xs + 0.2, y - 1.0, lw=1.4)
            label(d, xs + 4.6, y, text, ha="left")
        else:
            d.arrow(xs, y - 1.0, xd, y - 1.0, ls="--" if dashed else "-", lw=1.4)
            label(d, (xs + xd) / 2, y + (1.6 if two else 0.9), text)
        y -= 5.6 if two else 4.4
    if loop_top is not None:
        d.box(38.5, y + 1.2, 60.5, loop_top - y - 1.6, "none", ec=P["orange"], lw=1.0)


diagram("55-tc-vra-sequence", draw, w=13, h=14, xmax=100, ymax=138)

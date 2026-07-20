"""CH14 §1 TC와 작업기 사이의 상태 기반 대화 (명령/요청 ↔ 상태 보고)."""
from _common import diagram


def draw(d):
    P = d.P

    # TC 쪽
    d.box(3, 3, 26, 26, P["blue"])
    d.text(16, 26, "Task Controller", size=11, weight="bold")
    d.box(6, 17.5, 20, 5.5, P["chip"])
    d.text(16, 20.2, "TC-BAS  작업 데이터 기록", size=9)
    d.box(6, 11, 20, 5.5, P["chip"])
    d.text(16, 13.7, "TC-GEO  위치 기반 처방", size=9)
    d.box(6, 4.5, 20, 5.5, P["chip"])
    d.text(16, 7.2, "TC-SC  섹션 제어", size=9)

    # 작업기 쪽
    d.box(71, 3, 26, 26, P["green"])
    d.text(84, 26, "작업기 (TC 클라이언트)", size=11, weight="bold")
    d.box(74, 17.5, 20, 5.5, P["chip"])
    d.text(84, 20.2, "붐 · 섹션 · 탱크", size=9)
    d.box(74, 11, 20, 5.5, P["chip"])
    d.text(84, 13.7, "살포량 액추에이터", size=9)
    d.box(74, 4.5, 20, 5.5, P["chip"])
    d.text(84, 7.2, "센서 · 작업 상태", size=9)

    # 대화
    d.arrow(29, 22, 71, 22, color=P["orange"])
    d.text(50, 24.4, "명령 · 값 요청", size=9.5, color=P["orange"])

    d.arrow(71, 15, 29, 15, color=P["violet"])
    d.text(50, 17.4, "상태 업데이트 (프로세스 데이터)", size=9.5, color=P["violet"])

    d.arrow(71, 8, 29, 8, color=P["violet"])
    d.text(50, 10.4, "DDOP 업로드 (접속 시 1회)", size=9.5, color=P["violet"])


diagram("14-tc-roles", draw, w=12.5, h=4.2, ymax=32)

"""CH12 §3 로그 접두 태그로 문제 지점을 좁히는 지도."""
from _common import diagram


def draw(d):
    P = d.P

    rows = [
        ("[AC]", "주소 클레임", "선호 주소 충돌, 주소 탈취,\n주소 확보 실패", P["blue"]),
        ("[NM]", "네트워크 매니저", "송신 거절, 룩업 테이블 불일치", P["green"]),
        ("[TP] [ETP] [FP]", "멀티프레임 전송", "RTS/CTS 불일치, abort 수신,\n세션 개수 초과", P["purple"]),
        ("[VT]", "Virtual Terminal", "응답 타임아웃, 오브젝트 풀\n업로드 실패, VT 의 NACK", P["brown"]),
        ("[TC] [DDOP]", "Task Controller", "DDOP 구성 오류, TC 연결 상태", P["gray"]),
    ]

    top = 49.5
    h = 8.2
    for i, (tag, area, symptom, color) in enumerate(rows):
        y = top - (i + 1) * (h + 1.4)
        d.box(2, y, 22, h, color)
        d.text(13, y + h / 2, tag, size=9.4)
        d.box(26, y, 24, h, P["chip"])
        d.text(38, y + h / 2, area, size=9, color=P["dim"])
        d.box(52, y, 46, h, P["chip"])
        d.text(75, y + h / 2, symptom, size=8.6, color=P["dim"])
        d.arrow(24, y + h / 2, 26, y + h / 2, color=P["accent"], lw=1.2)
        d.arrow(50, y + h / 2, 52, y + h / 2, color=P["violet"], lw=1.2)


diagram("12-log-triage", draw, w=12, h=5.4, ymax=51)

"""43장 TC 클라이언트 연결 상태(구현 관점 정리용)와 상태 사이 조건 (light/dark PNG)."""
from _common import diagram

W, H = 19, 10
R1, R2 = 33, 11


def node(d, x, y, title, sub, color):
    d.box(x, y, W, H, d.P[color])
    d.text(x + W / 2, y + H / 2 + 1.7, title, size=11, weight="bold")
    d.text(x + W / 2, y + H / 2 - 1.8, sub, size=8.2)


def draw(d):
    P = d.P
    node(d, 2, R1, "주소 확보", "주소 클레임", "gray")
    node(d, 27, R1, "대기", "6 s 타이머", "gray")
    node(d, 52, R1, "TC 탐색", "선택한 TC의 TC Status", "blue")
    node(d, 77, R1, "연결 수립", "WSM · Client Task · 버전", "blue")
    node(d, 77, R2, "DDOP", "확인 → 전송 → Activate", "purple")
    node(d, 52, R2, "운용", "명령 응답 · 값 송신", "green")
    node(d, 2, R2, "셧다운", "Maintain Power · Deactivate", "brown")

    ym = R1 + H / 2
    d.arrow(21.2, ym, 26.8, ym)
    d.text(24, ym + 3.2, "클레임\n완료", size=8.2, color=P["accent"])
    d.arrow(46.2, ym, 51.8, ym)
    d.text(49, ym + 3.2, "6 s\n경과", size=8.2, color=P["accent"])
    d.arrow(71.2, ym, 76.8, ym)
    d.text(74, ym + 3.2, "TC Status\n수신", size=8.2, color=P["accent"])

    d.arrow(86.5, R1 - 0.2, 86.5, R2 + H + 0.2)
    d.text(88, (R1 + R2 + H) / 2, "버전 확인", size=8.2, color=P["accent"], ha="left")

    yb = R2 + H / 2
    d.arrow(76.8, yb, 71.2, yb)
    d.text(74, R2 - 2.4, "오류 없는\nActivate Response", size=8.2, color=P["accent"])

    d.arrow(61.5, R2 + H + 0.2, 61.5, R1 - 0.2, color=P["orange"], ls="--")
    d.text(60, (R1 + R2 + H) / 2, "TC Status\n6 s 끊김", size=8.2, color=P["orange"], ha="right")

    d.arrow(51.8, yb, 21.2, yb, color=P["violet"])
    d.text(36.5, yb + 2, "Key Switch Off", size=8.4, color=P["violet"])

    d.arrow(11.5, R2 + H + 0.2, 11.5, R1 - 0.2, color=P["violet"])
    d.text(13, (R1 + R2 + H) / 2, "Key Switch\nNot Off", size=8.2, color=P["violet"], ha="left")


diagram("43-client-connection-states", draw, w=12, h=5.4, xmax=100, ymax=45)

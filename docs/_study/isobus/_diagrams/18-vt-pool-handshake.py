"""18장 3절 사례 2: 작업기 ECU가 VT에 화면(오브젝트 풀)을 올리는 표준 절차 (light/dark PNG)."""
from _common import diagram

L, R = 22, 78
TOP = 61


def message(d, y, x1, x2, label, ls="-", lw=1.8):
    d.arrow(x1, y, x2, y, ls=ls, lw=lw)
    d.text((L + R) / 2, y + 1.7, label, size=9.8)


def draw(d):
    P = d.P
    for x, label in ((L, "작업기 ECU"), (R, "VT\n(트랙터 운전석 화면)")):
        d.box(x - 14, TOP, 28, 7, P["blue"])
        d.text(x, TOP + 3.5, label, size=10.5, weight="bold")
        d.ax.plot([x, x], [2, TOP], color=P["edge"], lw=1.1, ls="--", zorder=1)

    message(d, 55, L, R, "주소 클레임 (PGN 60928, 버스 전체에 브로드캐스트)")
    message(d, 48.5, R, L, "VT Status (1초마다 브로드캐스트)", ls="--")
    message(d, 42, L, R, "Get Memory (풀을 담을 메모리가 있는가?)")
    message(d, 35.5, R, L, "Get Memory 응답 (VT 버전, 메모리 여유)", ls="--")
    message(d, 29, L, R, "오브젝트 풀 전송 (TP·ETP로 나눠 보냄)", lw=3.0)
    message(d, 22.5, L, R, "End of Object Pool")
    message(d, 16, R, L, "End of Object Pool 응답", ls="--")

    d.box(R - 11, 5.5, 22, 6, P["green"], ec=P["accent"])
    d.text(R, 8.5, "화면 표시", size=10, weight="bold")


diagram("18-vt-pool-handshake", draw, w=11, h=7, xmax=100, ymax=70)

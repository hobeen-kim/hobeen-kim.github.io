"""CH17 §6 Annex F 명령-응답과 Annex H 활성화-응답(v6)의 대기·재시도 규칙 비교 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    def lane(x, name, col):
        d.box(x - 7, 50, 14, 4.6, col, lw=1.4)
        d.text(x, 52.3, name, size=10, weight="bold")
        d.ax.plot([x, x], [3, 50], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        d.text((x1 + x2) / 2, y + 1.3, label, size=8.2, color=color)

    # 왼쪽 패널: Annex F (WS -> VT)
    d.box(1, 1.5, 47, 57, P["chip"], ec=P["edge"], lw=1.0)
    d.text(24.5, 56.6, "명령과 응답 (Working Set -> VT)", size=10, weight="bold", color=P["accent"])
    WS_L, VT_L = 10, 39
    lane(WS_L, "Working Set", P["green"])
    lane(VT_L, "VT", P["blue"])

    hop(WS_L, VT_L, 45, "Change Numeric Value (A8)", P["accent"])
    hop(VT_L, WS_L, 41, "응답 (Error Code = 0)", P["dim"], ls="--")
    hop(WS_L, VT_L, 35, "Change Attribute (AF)", P["accent"])
    d.text(VT_L + 1.0, 30.6, "응답 없음", size=8, color=P["orange"], ha="left")
    # 1.5 s 구간 괄호
    d.ax.plot([5.2, 5.2], [35, 24], color=P["orange"], lw=1.4)
    d.ax.plot([5.2, 6.4], [35, 35], color=P["orange"], lw=1.4)
    d.ax.plot([5.2, 6.4], [24, 24], color=P["orange"], lw=1.4)
    d.text(4.6, 29.5, "1.5 s", size=8.5, color=P["orange"], ha="right")
    hop(WS_L, VT_L, 24, "다음 명령 허용 (재전송은 통상 3회 이하)", P["accent"])
    hop(VT_L, WS_L, 19, "응답", P["dim"], ls="--")

    # 오른쪽 패널: Annex H (VT -> WS), v6
    d.box(52, 1.5, 47, 57, P["chip"], ec=P["edge"], lw=1.0)
    d.text(75.5, 56.6, "활성화 메시지와 응답 (VT -> Working Set, v6 이상)", size=10, weight="bold", color=P["accent"])
    VT_R, WS_R = 61, 90
    lane(VT_R, "VT", P["blue"])
    lane(WS_R, "Working Set", P["green"])

    hop(VT_R, WS_R, 45, "Button Activation 누름 (TAN=1)", P["accent"])
    hop(WS_R, VT_R, 41, "응답 (TAN=1, 200 ms 이내)", P["dim"], ls="--")
    hop(VT_R, WS_R, 35, "Button Activation 뗌 (TAN=2)", P["accent"])
    d.text(WS_R - 1.0, 30.6, "응답 없음", size=8, color=P["orange"], ha="right")
    d.ax.plot([56.2, 56.2], [35, 26], color=P["orange"], lw=1.4)
    d.ax.plot([56.2, 57.4], [35, 35], color=P["orange"], lw=1.4)
    d.ax.plot([56.2, 57.4], [26, 26], color=P["orange"], lw=1.4)
    d.text(55.6, 30.5, "300 ms", size=8.5, color=P["orange"], ha="right")
    hop(VT_R, WS_R, 26, "재시도: 같은 데이터, 같은 TAN=2", P["violet"])
    d.text(75.5, 20.5, "재시도 최대 3회", size=8.5, color=P["violet"])
    d.box(60, 7, 31, 7.5, P["brown"], lw=1.2)
    d.text(75.5, 10.75, "그래도 응답이 없으면\nWorking Set unexpected shutdown 처리", size=8.8)

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="요청·통지"),
        Line2D([0], [0], color=P["dim"], lw=2.2, ls="--", label="응답"),
        Line2D([0], [0], color=P["violet"], lw=2.2, label="재시도"),
    ], loc="lower left", anchor=(0.012, 0.03))


diagram("17-response-timing", draw, w=14, h=7.4, xmax=100, ymax=60)

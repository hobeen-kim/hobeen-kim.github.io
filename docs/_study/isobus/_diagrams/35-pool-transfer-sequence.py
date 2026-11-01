"""35장 오브젝트 풀 전송 순서: Get Memory, Object Pool Transfer 여러 세션, End of Object Pool과 응답 (light/dark PNG)."""
from matplotlib.lines import Line2D

from _common import diagram

WS_X, VT_X = 22, 78


def message(d, y, label, sub, to_vt=True, color=None):
    x1, x2 = (WS_X, VT_X) if to_vt else (VT_X, WS_X)
    d.arrow(x1, y, x2, y, color=color)
    d.text(50, y + 1.6, label, size=9)
    if sub:
        d.text(50, y - 1.6, sub, size=8, color=d.P["dim"])


def draw(d):
    P = d.P
    # 참여자와 생명선
    for x, name in [(WS_X, "WS (Working Set Master)"), (VT_X, "VT")]:
        d.box(x - 13, 52, 26, 6, P["blue"])
        d.text(x, 55, name, size=10, weight="bold")
        d.ax.add_line(Line2D([x, x], [3, 52], color=P["edge"], lw=1.2, ls="--", zorder=1))

    message(d, 47, "Get Memory", "Memory Required = 보낼 풀(또는 갱신분) 크기")
    message(d, 41, "Get Memory response", "VT 버전, 메모리 여유", to_vt=False)
    message(d, 34.5, "Object Pool Transfer (0x11 + 레코드)", "세션 1, 응답 없음")
    message(d, 28.5, "Object Pool Transfer (0x11 + 레코드)", "세션 2, 응답 없음")
    message(d, 22, "End of Object Pool (12 FF FF FF FF FF FF FF)", "이것으로 전부다")
    message(d, 8, "End of Object Pool response (0x12 ...)", "오류 코드, 결함 오브젝트 ID", to_vt=False)

    # 여러 세션 묶음 표시
    d.ax.add_line(Line2D([WS_X - 3, WS_X - 3], [27, 37], color=P["orange"], lw=1.6, zorder=3))
    d.text(WS_X - 4, 32, "세션 여러 개\n이어 보내기 가능", size=8.5, color=P["orange"], ha="right")

    # VT 파싱 구간
    d.box(VT_X - 1.2, 10.5, 2.4, 9.5, P["brown"])
    d.text(VT_X + 2.5, 15.2, "파싱 중\nVT Status의\nparsing 비트 = 1", size=8.5, color=P["dim"], ha="left")


diagram("35-pool-transfer-sequence", draw, w=12, h=7.2, xmax=100, ymax=60)

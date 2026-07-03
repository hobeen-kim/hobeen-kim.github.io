"""CH27 실전 워크플로우 — 알림→트레이스→프로파일→개선 확인 (light/dark PNG)."""
from _common import diagram
from _common import Line2D


def draw(d):
    P = d.P

    def step(cx, cy, w, h, n, title, sub, c, ec=None):
        d.box(cx - w / 2, cy - h / 2, w, h, c, ec=ec or P["edge"], lw=1.6)
        d.text(cx - w / 2 + 3, cy + h / 2 - 2.4, str(n), size=12,
               weight="bold", color=P["accent"])
        d.text(cx, cy + 1.2, title, size=10, weight="bold")
        d.text(cx, cy - 2.6, sub, size=8, color=P["dim"])

    W, H = 21, 11
    TOP, BOT = 38, 15

    # 상단 행: 1 2 3 4
    step(14, TOP, W, H, 1, "Alertmanager", "알림 발화\n(p99 SLO 위반)", P["brown"])
    step(38, TOP, W, H, 2, "Tempo", "느린 트레이스 조회\n(exemplar 진입)", P["green"])
    step(62, TOP, W, H, 3, "느린 스팬 특정", "어느 요청·스팬에서", P["green"])
    step(86, TOP, W, H, 4, "Pyroscope", "span profile 조회", P["purple"], ec=P["accent"])

    # 하단 행 (역방향): 5 6 7
    step(86, BOT, W, H, 5, "핫패스 함수 특정", "가장 넓은 프레임", P["purple"], ec=P["accent"])
    step(50, BOT, W, H, 6, "코드 수정 → 재배포", "원인 함수 최적화", P["blue"])
    step(14, BOT, W, H, 7, "diff view", "개선 확인\n(전/후 비교)", P["brown"], ec=P["orange"])

    # 상단 화살표
    d.arrow(24.5, TOP, 27.5, TOP, color=P["accent"], lw=2.0)
    d.arrow(48.5, TOP, 51.5, TOP, color=P["accent"], lw=2.0)
    d.arrow(72.5, TOP, 75.5, TOP, color=P["accent"], lw=2.0)
    # 4 → 5 (하강)
    d.arrow(86, TOP - H / 2, 86, BOT + H / 2, color=P["orange"], lw=2.2)
    # 하단 화살표 (우→좌)
    d.arrow(75.5, BOT, 60.5, BOT, color=P["accent"], lw=2.0)
    d.arrow(39.5, BOT, 24.5, BOT, color=P["accent"], lw=2.0)

    leg = [
        Line2D([0], [0], color=P["accent"], lw=2.2, label="신호 간 이동(drill-down)"),
        Line2D([0], [0], color=P["orange"], lw=2.2, label="트레이스 → 프로파일 진입"),
    ]
    d.legend(leg, anchor=(0.005, 0.02))


diagram("27-workflow", draw, w=13, h=6, ymax=48)

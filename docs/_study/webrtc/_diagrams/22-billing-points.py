"""CH22 §4 KVS WebRTC 과금 지점 — 어느 경로에서 무엇이 계량되는가 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    # 양 끝 피어
    d.box(1.5, 6, 14, 30, P["green"])
    d.text(8.5, 23, "디바이스", size=10, weight="bold")
    d.text(8.5, 19, "(master)", size=8.2, color=P["dim"])
    d.box(84.5, 6, 14, 30, P["blue"])
    d.text(91.5, 23, "운영자", size=10, weight="bold")
    d.text(91.5, 19, "(viewer)", size=8.2, color=P["dim"])

    # 시그널링 채널
    d.box(36, 39, 28, 10, P["purple"])
    d.text(50, 45.5, "시그널링 채널", size=9.6, weight="bold")
    d.text(50, 41.5, "활성 채널/월 · 메시지/100만 건", size=8, color=P["orange"])
    d.arrow(12, 36.3, 35.8, 43, color=P["dim"], ls="--", lw=1.2, style="<|-|>")
    d.arrow(88, 36.3, 64.2, 43, color=P["dim"], ls="--", lw=1.2, style="<|-|>")

    # 직접 P2P
    d.arrow(15.8, 31, 84.2, 31, color=P["accent"], lw=2.0, style="<|-|>")
    d.text(50, 33, "직접 P2P (host / srflx)", size=8.6, color=P["accent"])
    d.text(50, 28.6, "KVS 미디어 요금 없음", size=8, color=P["dim"])

    # TURN
    d.box(38, 15.5, 24, 9, P["gray"])
    d.text(50, 21.5, "KVS TURN", size=9.4, weight="bold")
    d.text(50, 17.8, "TURN 분 + 인터넷 데이터 전송", size=7.8, color=P["orange"])
    d.arrow(15.8, 20, 37.8, 20, color=P["violet"], lw=1.6, style="<|-|>")
    d.arrow(62.2, 20, 84.2, 20, color=P["violet"], lw=1.6, style="<|-|>")
    d.text(26.8, 21.6, "relay", size=7.8, color=P["violet"])
    d.text(73.2, 21.6, "relay", size=7.8, color=P["violet"])

    # 저장 모드
    d.box(33, 2, 34, 10, P["brown"])
    d.text(50, 8.6, "storage 세션 → Video Stream", size=9.2, weight="bold")
    d.text(50, 4.8, "녹화 분 · 실시간 viewer 분 · 저장 GB-월", size=7.8, color=P["orange"])
    d.arrow(15.8, 8, 32.8, 8, color=P["violet"], lw=1.4, ls=(0, (2, 2)))
    d.arrow(67.2, 8, 84.2, 8, color=P["violet"], lw=1.4, ls=(0, (2, 2)), style="<|-|>")
    d.text(24.3, 9.6, "저장 모드", size=7.6, color=P["violet"])

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=0, marker="s", markersize=6, label="과금 항목"),
    ], loc="upper left", anchor=(0.005, 0.995))


diagram("22-billing-points", draw, w=13, h=6.2, ymax=50)

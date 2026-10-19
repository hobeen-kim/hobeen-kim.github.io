"""CH22 §7 장시간 디바이스의 만료 시계들 — 시그널링 1시간 · GO_AWAY · TURN 300초 · IoT 자격증명 (light/dark PNG)."""
from _common import diagram


def X(m):
    return 22 + m  # 0~75분 → x 22~97


def draw(d):
    P = d.P

    # 시간축
    d.ax.plot([X(0), X(75)], [4, 4], color=P["edge"], lw=1.2)
    for m in range(0, 76, 15):
        d.ax.plot([X(m), X(m)], [3.3, 4.7], color=P["edge"], lw=1.2)
        d.text(X(m), 1.6, "0" if m == 0 else f"{m}분", size=8, color=P["dim"])

    lanes = [
        (37, "시그널링 WSS", "(최대 1시간 · idle 10분)"),
        (28, "GO_AWAY 대응", "(유예 60초)"),
        (19, "TURN 자격증명", "(Ttl 300초 고정)"),
        (10, "IoT 임시 자격증명", "(role alias 기본 3,600초)"),
    ]
    for y, name, sub in lanes:
        d.text(1.5, y + 1.3, name, size=9.2, weight="bold", ha="left")
        d.text(1.5, y - 1.8, sub, size=7.6, color=P["dim"], ha="left")
        d.ax.plot([X(0), X(75)], [y, y], color=P["edge"], lw=0.6, ls=(0, (2, 3)), zorder=1)

    # 1시간 하드 리밋
    d.ax.plot([X(60), X(60)], [6, 42], color=P["orange"], lw=1.4, ls="--", zorder=2)
    d.text(X(60), 43.3, "연결 60분 한도", size=8, color=P["orange"])

    # 시그널링 레인
    d.box(X(0), 35.3, 40, 3.4, P["blue"], ec=P["accent"], lw=1.2)
    d.box(X(40.6), 35.3, 34.4, 3.4, P["blue"], ec=P["accent"], lw=1.2)
    d.text(X(20), 37, "WebSocket 연결 #1", size=7.8)
    d.text(X(67.5), 37, "#2", size=7.8)
    d.arrow(X(40.3), 41, X(40.3), 39, color=P["accent"], lw=1.4)
    d.text(X(31), 41, "40분±지터 선제 재연결", size=7.6, color=P["accent"])

    # GO_AWAY 레인
    d.ax.plot([X(32), X(32)], [26, 30], color=P["violet"], lw=2.2)
    d.text(X(31), 30.4, "GO_AWAY 수신", size=7.6, color=P["violet"], ha="right")
    d.box(X(32), 26.6, 1.0, 2.8, P["purple"], ec=P["violet"], lw=1.0)
    d.text(X(34), 30.4, "60초 안에 메시지 처리 후 재연결", size=7.6, color=P["dim"], ha="left")

    # TURN 레인: 5분마다 재발급
    for k in range(15):
        m0 = k * 5
        d.box(X(m0) + 0.25, 17.6, 4.5, 2.8, P["gray"], ec=P["edge"], lw=0.9)
    d.text(X(37.5), 22.6, "새 PeerConnection·ICE restart 때마다 GetIceServerConfig 재호출",
           size=7.6, color=P["dim"])

    # IoT 자격증명 레인
    d.box(X(0), 8.3, 60, 3.4, P["green"], ec=P["edge"], lw=1.0)
    d.box(X(50), 8.3, 25, 3.4, P["green"], ec=P["accent"], lw=1.2)
    d.text(X(24), 10, "임시 자격증명 #1 (expiration)", size=7.6)
    d.text(X(67.5), 10, "#2", size=7.6)
    d.arrow(X(50), 14.6, X(50), 12, color=P["accent"], lw=1.4)
    d.text(X(43), 14.8, "만료 전 갱신", size=7.6, color=P["accent"])


diagram("22-connection-timeline", draw, w=13, h=5.8, ymax=45)

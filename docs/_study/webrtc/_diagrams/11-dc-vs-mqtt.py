"""CH11 §5 DataChannel vs MQTT(AWS IoT Core) 제어 채널 역할 분담 — (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 노드
    d.box(2, 30, 22, 14, P["blue"])
    d.text(13, 39.5, "운영자 브라우저", size=10.5, weight="bold")
    d.text(13, 35, "영상 시청 · 조이스틱", size=8, color=P["dim"])

    d.box(76, 30, 22, 14, P["green"])
    d.text(87, 39.5, "농기계 · 로봇", size=10.5, weight="bold")
    d.text(87, 35, "제어 루프 · 워치독", size=8, color=P["dim"])

    d.box(2, 3, 22, 12, P["brown"])
    d.text(13, 10.5, "백엔드 API", size=10.5, weight="bold")
    d.text(13, 6.5, "인가 · 감사 로그", size=8, color=P["dim"])

    d.box(39, 3, 24, 12, P["purple"])
    d.text(51, 10.5, "AWS IoT Core", size=10.5, weight="bold")
    d.text(51, 6.5, "MQTT · Shadow · Jobs", size=8, color=P["dim"])

    # DataChannel (P2P)
    d.arrow(24, 40, 76, 40, color=P["accent"], lw=2.4, style="<|-|>")
    d.text(50, 43.5, "DataChannel (P2P, 세션 중에만)", size=9.5, weight="bold", color=P["accent"])
    d.text(50, 37.2, "조이스틱 · PTZ 연속 조작 (unordered · 재전송 0)\n최신값만 유효 · 수십 ms", size=8,
           color=P["dim"])

    # MQTT 경로
    d.arrow(13, 30, 13, 15, color=P["orange"], lw=1.6)
    d.text(14.5, 22.5, "명령 요청\n(HTTPS)", size=8, color=P["orange"], ha="left")
    d.arrow(24, 9, 39, 9, color=P["orange"], lw=1.6)
    d.text(31.5, 10.8, "publish", size=8, color=P["orange"])
    d.arrow(63, 11, 80, 30, color=P["orange"], lw=1.8, style="<|-|>")
    d.text(76.5, 19, "모드 변경 · 작업 명령 (QoS 1)\n텔레메트리 · 상태\nShadow desired / reported\n오프라인 큐(영구 세션)",
           size=7.8, color=P["orange"], ha="left")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.5, label="저지연 조작"),
        Line2D([0], [0], color=P["orange"], lw=2.5, label="신뢰성 있는 명령 · 상태"),
    ], loc="upper left", anchor=(0.005, 0.995), fontsize=7.8)


diagram("11-dc-vs-mqtt", draw, w=12.5, h=5.8, ymax=48)

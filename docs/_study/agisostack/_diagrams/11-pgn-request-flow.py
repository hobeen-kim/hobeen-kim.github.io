"""CH11 §3 PGN 요청 수신 경로 — 콜백이 있으면 앱으로, 없으면 스택이 NACK."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 20, 20, 12, P["blue"])
    d.text(12, 26, "요청한 CF", size=9.6)

    d.text(28, 28.6, "PGN 59904\n(0xEA00)", size=8.6, color=P["dim"])
    d.arrow(22, 26, 34, 26, color=P["accent"])

    d.box(34, 18, 30, 16, P["green"])
    d.text(49, 30.5, "ParameterGroupNumberRequestProtocol", size=8.8)
    d.text(49, 24.5, "내부 CF마다 1개\nget_pgn_request_protocol()", size=8.6, color=P["dim"])

    d.box(72, 24, 26, 13, P["purple"])
    d.text(85, 33.5, "등록된 콜백 있음", size=9.2)
    d.text(85, 28.5, "앱이 데이터 송신 또는\nacknowledge / acknowledgeType 지정", size=8.4, color=P["dim"])

    d.box(72, 8, 26, 12, P["gray"])
    d.text(85, 16.5, "등록된 콜백 없음", size=9.2)
    d.text(85, 12, "스택이 자동 NACK\n(목적지 지정 요청만)", size=8.4, color=P["dim"])

    d.arrow(64, 28, 72, 30, color=P["violet"])
    d.arrow(64, 24, 72, 15, color=P["orange"])
    d.text(68.5, 31.5, "true", size=8.2, color=P["dim"])
    d.text(69.5, 20.5, "false", size=8.2, color=P["dim"])

    # 응답 경로 (아래쪽으로 우회)
    d.arrow(85, 8, 85, 3.5, color=P["accent"], style="-")
    d.arrow(85, 3.5, 12, 3.5, color=P["accent"], style="-")
    d.arrow(12, 3.5, 12, 20, color=P["accent"])
    d.text(49, 5.6, "응답 / ACK / NACK 은 요청한 CF 로", size=8.8, color=P["dim"])


diagram("11-pgn-request-flow", draw, w=13, h=4.7, ymax=39)

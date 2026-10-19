"""CH24 §1 Stage·Participant Token 구조 — 백엔드가 역할별 토큰 발급, 디바이스는 WHIP 퍼블리시, 운영자는 구독 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 백엔드
    d.box(2, 41, 25, 11, P["green"], lw=1.5)
    d.text(14.5, 46.5, "백엔드\n(토큰 발급 API)", size=10, weight="bold")

    # 컨트롤 플레인
    d.box(60, 41, 36, 11, P["purple"], lw=1.5)
    d.text(78, 46.5, "IVS Real-Time 컨트롤 플레인\n(ivsrealtime.ap-northeast-2)", size=10,
           weight="bold")
    d.arrow(27, 49, 60, 49, color=P["accent"])
    d.text(43.5, 51, "CreateParticipantToken", size=8.6, color=P["accent"])
    d.arrow(60, 44, 27, 44, color=P["dim"], ls="--")
    d.text(43.5, 42, "token · participantId · expirationTime", size=8.4,
           color=P["dim"])

    # 클라이언트
    d.box(6, 22, 18, 9, P["brown"])
    d.text(15, 26.5, "농기계 디바이스\n토큰: PUBLISH · 60분", size=8.8)
    d.box(2, 4, 25, 9, P["blue"])
    d.text(14.5, 8.5, "운영자 브라우저\n토큰: SUBSCRIBE · role=operator", size=8.8)

    # 토큰 배포
    d.arrow(15, 41, 15, 31, color=P["orange"])
    d.text(16.2, 36, "MQTT", size=8.2, color=P["orange"], ha="left")
    d.arrow(3.6, 41, 3.6, 13, color=P["orange"])
    d.text(4.8, 17.5, "HTTPS", size=8.2, color=P["orange"], ha="left")

    # 스테이지
    d.box(40, 2, 56, 31, P["gray"], lw=1.4)
    d.text(68, 30.6, "Stage (데이터 플레인은 글로벌)", size=9.6, weight="bold")
    chips = [
        (20, 7, "publisher: 스테이지당 최대 12 (조정 불가)"),
        (11.2, 7, "subscriber: 스테이지당 최대 10,000 (조정 가능)"),
        (4, 5.6, "simulcast 레이어를 구독자 상황에 맞춰 선택"),
    ]
    for y, h, label in chips:
        d.box(43, y, 50, h, P["chip"])
        d.text(68, y + h / 2, label, size=8.8)

    d.arrow(24, 26.5, 40, 26.5, color=P["accent"], lw=2.4)
    d.text(32, 28.3, "WHIP 퍼블리시", size=8.3, color=P["accent"])
    d.arrow(40, 8.5, 27, 8.5, color=P["accent"], lw=2.4)
    d.text(33.5, 10.2, "WebRTC 구독", size=8.3, color=P["accent"])

    d.arrow(86, 41, 86, 33, color=P["violet"], ls="--")
    d.text(87.2, 37, "스테이지 리소스 (리전)", size=8.3, color=P["violet"], ha="left")


diagram("24-stage-token", draw, w=13, h=7.2, ymax=54)

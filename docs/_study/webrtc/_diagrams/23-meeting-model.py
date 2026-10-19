"""CH23 §2 Chime SDK 회의 모델 — 백엔드가 미팅·참석자 생성, JoinToken 전달, 클라이언트가 미디어 서비스(SFU)에 접속 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 백엔드
    d.box(3, 41, 22, 10, P["green"], lw=1.5)
    d.text(14, 46, "백엔드\n(Node.js · Spring)", size=10, weight="bold")

    # 컨트롤 플레인
    d.box(58, 41, 38, 10, P["purple"], lw=1.5)
    d.text(77, 46, "Chime SDK 컨트롤 플레인\n(meetings-chime.ap-northeast-2)", size=10,
           weight="bold")

    d.arrow(25, 48.2, 58, 48.2, color=P["accent"])
    d.text(41.5, 50.2, "CreateMeeting(MediaRegion) · CreateAttendee", size=8.6,
           color=P["accent"])
    d.arrow(58, 43.6, 25, 43.6, color=P["dim"], ls="--")
    d.text(41.5, 41.6, "MediaPlacement · JoinToken", size=8.6, color=P["dim"])

    # 클라이언트
    clients = [
        (24.5, "운영자 브라우저\n(amazon-chime-sdk-js)", P["blue"]),
        (13.5, "운영자 모바일\n(Android · iOS SDK)", P["blue"]),
        (2.5, "농기계 디바이스\n(C++ 시그널링 + WebRTC 직접)", P["brown"]),
    ]
    for y, label, col in clients:
        d.box(3, y, 24, 8.5, col)
        d.text(15, y + 4.25, label, size=9)

    # JoinToken 전달
    d.arrow(14, 41, 14, 33.4, color=P["orange"])
    d.text(15.2, 37.2, "JoinToken 전달\n(HTTPS · MQTT)", size=8.4, color=P["orange"],
           ha="left")

    # 미디어 서비스 그룹
    d.box(50, 2, 46, 31.5, P["gray"], lw=1.4)
    d.text(73, 31, "Chime 미디어 서비스 (MediaRegion: ap-northeast-2)", size=9.4,
           weight="bold")
    chips = [
        (21.2, "시그널링 (secure WebSocket)"),
        (12.4, "SFU: 비디오 선택 전달 (회의당 최대 25개)"),
        (3.6, "오디오 믹서: Opus 믹스 (자기 소리 제외)"),
    ]
    for y, label in chips:
        d.box(53, y, 40, 7, P["chip"])
        d.text(73, y + 3.5, label, size=9)

    # 클라이언트 ↔ 미디어 서비스
    for y, _, _ in clients:
        d.arrow(27, y + 4.25, 50, y + 4.25, color=P["accent"], style="<|-|>")
    d.text(38.5, 30.6, "WSS + DTLS-SRTP", size=8.4, color=P["accent"])

    # 컨트롤 플레인 → 미디어 서비스
    d.arrow(85, 41, 85, 33.5, color=P["violet"], ls="--")
    d.text(86.2, 37.2, "미팅 호스팅 위치", size=8.4, color=P["violet"], ha="left")


diagram("23-meeting-model", draw, w=13, h=7.2, ymax=53)

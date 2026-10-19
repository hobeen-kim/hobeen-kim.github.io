"""CH24 §4 Composition과 녹화 — 서버 측 합성(IVS 채널·S3)과 개별 참가자 녹화(S3) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 스테이지
    d.box(2, 5, 25, 41, P["gray"], lw=1.5)
    d.text(14.5, 43.2, "Stage", size=10, weight="bold")
    pubs = [
        (32, "트랙터 전방 카메라\n(WHIP)", P["brown"]),
        (20.5, "작업기 카메라\n(WHIP)", P["brown"]),
        (9, "운영자\n(Web SDK, 음성)", P["blue"]),
    ]
    for y, label, col in pubs:
        d.box(4.5, y, 20, 8.5, col)
        d.text(14.5, y + 4.25, label, size=8.8)

    # 서버 측 합성
    d.box(37, 29, 27, 15, P["purple"], lw=1.5)
    d.text(50.5, 36.5, "서버 측 합성\n(StartComposition)\n레이아웃: grid · PiP", size=9.2,
           weight="bold")
    d.arrow(27, 36.5, 37, 36.5, color=P["accent"], lw=2.2)

    # 합성 목적지
    d.box(73, 38, 25, 9, P["green"])
    d.text(85.5, 42.5, "IVS 저지연 채널\n→ HLS 대규모 시청", size=8.8)
    d.box(73, 26, 25, 9, P["brown"])
    d.text(85.5, 30.5, "S3 (StorageConfiguration)\n합성 영상 HLS", size=8.8)
    d.arrow(64, 39.5, 73, 42.5, color=P["accent"])
    d.arrow(64, 33.5, 73, 30.5, color=P["accent"])
    d.text(68.5, 36.5, "destination\n최대 2개", size=7.8, color=P["accent"])

    # 개별 참가자 녹화
    d.box(37, 5, 27, 14, P["purple"], lw=1.5)
    d.text(50.5, 12, "개별 참가자 녹화\n(autoParticipantRecording\nConfiguration)", size=9,
           weight="bold")
    d.arrow(27, 12, 37, 12, color=P["orange"], lw=2.2)

    d.box(73, 5, 25, 14, P["brown"])
    d.text(85.5, 12, "S3: publisher별\nHLS(fMP4) + 썸네일\n+ 메타데이터 JSON", size=8.8)
    d.arrow(64, 12, 73, 12, color=P["orange"])
    d.text(68.5, 14.2, "같은 리전\n버킷", size=7.8, color=P["orange"])


diagram("24-composition-recording", draw, w=13, h=6.0, ymax=48.5)

"""CH23 §5 Media Pipelines 종류 — capture·concatenation·live connector·media stream·media insights와 목적지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 미팅
    d.box(2, 19, 19, 19, P["purple"], lw=1.6)
    d.text(11.5, 28.5, "Chime SDK 미팅\n(SFU · 오디오 믹서)", size=10, weight="bold")

    rows = [
        (45, "media capture\n(합성 옵션: GridView 등)", P["blue"],
         "S3: 스트림별 조각 파일\n+ 미팅 이벤트 · 데이터 메시지", P["brown"]),
        (35, "media concatenation", P["blue"],
         "S3: 하나로 합친 파일", P["brown"]),
        (23, "media live connector\n(합성 옵션: GridView 등)", P["blue"],
         "RTMP(S) → IVS · YouTube · Twitch\n(H.264 HD/FHD · AAC)", P["green"]),
        (13, "media stream", P["blue"],
         "KVS 스트림 풀\n(참석자별 오디오 + 믹스 오디오)", P["gray"]),
        (3, "media insights\n(call analytics)", P["blue"],
         "Transcribe · 음성 분석 · S3 녹음", P["gray"]),
    ]
    for y, name, col, dest, dcol in rows:
        d.box(31, y, 25, 7, col)
        d.text(43.5, y + 3.5, name, size=8.8)
        d.box(64, y, 33, 7, dcol)
        d.text(80.5, y + 3.5, dest, size=8.6)
        d.arrow(56, y + 3.5, 64, y + 3.5, color=P["accent"])

    # 미팅 → capture · live connector · media stream
    d.arrow(21, 35, 31, 48.5, color=P["accent"], lw=1.6)
    d.arrow(21, 28.5, 31, 26.5, color=P["accent"], lw=1.6)
    d.arrow(21, 22, 31, 16.5, color=P["accent"], lw=1.6)

    # capture → concatenation
    d.arrow(43.5, 45, 43.5, 42, color=P["orange"], lw=1.6)
    d.text(44.6, 43.5, "capture 결과를 소스로", size=7.8, color=P["orange"],
           ha="left")

    # KVS → media insights
    d.arrow(68, 13, 52, 10, color=P["violet"], lw=1.4, ls="--", rad=-0.15)
    d.text(70, 11.2, "KVS 스트림을 소스로", size=7.8, color=P["violet"],
           ha="left")


diagram("23-media-pipelines", draw, w=13, h=6.8, ymax=53)

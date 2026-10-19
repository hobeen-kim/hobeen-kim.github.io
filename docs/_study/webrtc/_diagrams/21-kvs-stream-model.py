"""CH21 §1 KVS Video Streams 모델 — Producer → 프래그먼트 타임라인(보존 기간) → 소비 API (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 생산자
    d.box(1.5, 21, 19, 12, P["green"])
    d.text(11, 29, "농기계 카메라", size=10.5, weight="bold")
    d.text(11, 24.8, "(Producer SDK · kvssink)", size=8.5, color=P["dim"])

    d.arrow(21, 27, 28.5, 27, color=P["accent"])
    d.text(24.8, 30.2, "PutMedia", size=8.5, color=P["accent"])
    d.text(24.8, 23.6, "MKV\n장기 연결", size=7.8, color=P["dim"])

    # 스트림 그룹
    d.box(29, 7, 39, 37, P["gray"])
    d.text(48.5, 41, "Kinesis Video Stream (tractor-001)", size=9.5, weight="bold")

    # 프래그먼트 칩
    xs = [31 + i * 5.2 for i in range(7)]
    for i, x in enumerate(xs):
        expired = i == 0
        d.box(x, 23, 4.4, 7, P["chip"], ec=P["edge"] if expired else P["accent"],
              lw=1.0 if expired else 1.4, alpha=0.55 if expired else 1.0)
        d.text(x + 2.2, 26.5, f"F{1001 + i}", size=7.2,
               color=P["dim"] if expired else P["text"])
    d.text(33.2, 20.6, "만료", size=7.8, color=P["dim"])
    d.text(48.5, 16.2, "프래그먼트 = 키프레임부터 시작 (1~20초)", size=8.2, color=P["dim"])
    d.text(48.5, 12.4, "producer / server timestamp · 프래그먼트 번호", size=8.2, color=P["dim"])

    # 보존 기간 브래킷
    x0, x1 = xs[1], xs[-1] + 4.4
    d.ax.plot([x0, x0, x1, x1], [32, 34, 34, 32], color=P["orange"], lw=1.4, zorder=3)
    d.text((x0 + x1) / 2, 36.4, "DataRetentionInHours (예: 168시간)", size=8.2,
           color=P["orange"])
    d.text(xs[-1] + 2.2, 20.6, "최신", size=7.8, color=P["dim"])

    # 소비 API
    consumers = [
        (37, "HLS / DASH", "LIVE · LIVE_REPLAY · ON_DEMAND", P["blue"]),
        (27, "GetClip", "MP4 · 100MB / 200프래그먼트", P["purple"]),
        (17, "GetMedia", "MKV 스트림 (분석 파이프라인)", P["brown"]),
        (7, "GetImages", "프레임 → JPEG/PNG", P["blue"]),
    ]
    for y, name, sub, col in consumers:
        d.box(74, y - 3.6, 24.5, 7.6, col)
        d.text(86.25, y + 1.2, name, size=9.5, weight="bold")
        d.text(86.25, y - 1.8, sub, size=7.6, color=P["dim"])
        d.arrow(68.2, 25.5, 73.6, y, color=P["violet"], lw=1.3)
    d.text(71, 46.5, "GetDataEndpoint로 API별 엔드포인트 조회", size=8,
           color=P["violet"])


diagram("21-kvs-stream-model", draw, w=13, h=6.2, ymax=49)

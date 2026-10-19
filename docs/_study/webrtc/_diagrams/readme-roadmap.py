"""README 학습 로드맵 — S1~S8 단계 체인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("S1", "WebRTC 기초 (01~03)",
         ["왜 WebRTC인가", "API", "시그널링"], P["gray"]),
        ("S2", "연결 수립 (04~07)",
         ["SDP·JSEP", "NAT·STUN", "ICE", "TURN"], P["blue"]),
        ("S3", "미디어와 데이터 전송 (08~11)",
         ["RTP·코덱", "품질·지연", "DTLS-SRTP", "DataChannel"], P["green"]),
        ("S4", "아키텍처와 운영 (12~15)",
         ["SFU 토폴로지", "디바이스 구현", "WHIP/WHEP", "모니터링"], P["brown"]),
        ("S5", "AWS 개관과 KVS 기초 (16~18)",
         ["서비스 지도", "KVS 아키텍처", "시그널링 API"], P["purple"]),
        ("S6", "KVS 구현과 운영 (19~22)",
         ["C SDK", "뷰어·백엔드", "인제스트·저장", "운영·비용"], P["green"]),
        ("S7", "Chime SDK · IVS (23~24)",
         ["Chime SDK", "IVS Real-Time"], P["blue"]),
        ("S8", "캡스톤 (25)",
         ["농기계 원격 영상·제어 플랫폼"], P["brown"]),
    ]

    col_x = [27, 73]
    row_cy = [43, 32, 21, 10]
    BW, BH = 42, 9.2

    def wrap_chain(steps):
        if len(steps) <= 3:
            return "  →  ".join(steps)
        mid = (len(steps) + 1) // 2
        return "  →  ".join(steps[:mid]) + "  →\n" + "  →  ".join(steps[mid:])

    positions = []
    for i, (tag, title, steps, fc) in enumerate(stages):
        row, col = i // 2, i % 2
        cx, cy = col_x[col], row_cy[row]
        positions.append((cx, cy))
        last = tag == "S8"
        ec = P["accent"] if last else P["edge"]
        lw = 2.2 if last else 1.5
        d.box(cx - BW / 2, cy - BH / 2, BW, BH, fc, ec=ec, lw=lw)
        d.box(cx - BW / 2 + 1.2, cy + BH / 2 - 3.4, 6.5, 2.6, P["bg"], ec=ec, lw=1.2, r=0.02)
        d.text(cx - BW / 2 + 4.45, cy + BH / 2 - 2.1, tag, size=9.5, weight="bold",
               color=P["accent"] if last else P["text"])
        d.text(cx + 3, cy + BH / 2 - 2.1, title, size=10.5, weight="bold")
        d.text(cx, cy - 1.3, wrap_chain(steps), size=8.2, color=P["dim"])

    for i in range(len(stages) - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i + 1]
        if i % 2 == 0:
            d.arrow(x1 + BW / 2, y1, x2 - BW / 2, y2, color=P["accent"], lw=2.0)
        else:
            d.arrow(x1, y1 - BH / 2, x2, y2 + BH / 2, color=P["accent"], lw=2.0)


diagram("readme-roadmap", draw, w=15, h=7.5, ymax=49)

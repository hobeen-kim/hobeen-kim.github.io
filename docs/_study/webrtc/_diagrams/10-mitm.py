"""CH10 §4 신뢰 모델 — 정상 시그널링 vs SDP를 바꿔치는 시그널링(MITM) — (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def panel(x0, title, ec):
        d.box(x0, 2, 47, 46, P["gray"], ec=ec, lw=1.6)
        d.text(x0 + 23.5, 45, title, size=10.5, weight="bold", color=ec)

    # 왼쪽: 정상
    panel(1, "정상: 시그널링이 SDP를 그대로 전달", P["accent"])
    d.box(3, 28, 12, 8, P["blue"])
    d.text(9, 32, "브라우저\n(인증서 A)", size=8.5)
    d.box(18.5, 28, 12, 8, P["brown"])
    d.text(24.5, 32, "시그널링", size=8.5, weight="bold")
    d.box(34, 28, 12, 8, P["green"])
    d.text(40, 32, "디바이스\n(인증서 B)", size=8.5)
    d.arrow(15, 34.5, 18.5, 34.5, color=P["orange"], lw=1.3)
    d.arrow(30.5, 34.5, 34, 34.5, color=P["orange"], lw=1.3)
    d.text(24.5, 39, "fingerprint A ↔ B 원본 그대로", size=7.8, color=P["orange"])
    d.arrow(9, 28, 40, 28, color=P["accent"], lw=2.2, style="<|-|>", rad=0.5)
    d.text(24.5, 17, "DTLS 1개 (A ↔ B)", size=8.5, color=P["accent"], weight="bold")
    d.text(24.5, 7, "양쪽 모두 해시 일치 → 종단 간 암호화", size=8, color=P["dim"])

    # 오른쪽: 공격
    panel(52, "공격: 시그널링이 SDP를 바꿔치기", P["orange"])
    d.box(54, 28, 12, 8, P["blue"])
    d.text(60, 32, "브라우저\n(인증서 A)", size=8.5)
    d.box(69.5, 28, 12, 8, P["brown"], ec=P["orange"], lw=1.8)
    d.text(75.5, 32, "시그널링\n(탈취·악의)", size=8.5, weight="bold")
    d.box(85, 28, 12, 8, P["green"])
    d.text(91, 32, "디바이스\n(인증서 B)", size=8.5)
    d.arrow(66, 34.5, 69.5, 34.5, color=P["orange"], lw=1.3)
    d.arrow(81.5, 34.5, 85, 34.5, color=P["orange"], lw=1.3)
    d.text(75.5, 39.5, "B → M, A → M' 으로 교체\n후보도 공격자 주소로", size=7.8, color=P["orange"])

    d.box(68, 10, 15, 8, P["purple"], ec=P["orange"], lw=1.6)
    d.text(75.5, 14, "공격자 릴레이\n(인증서 M · M')", size=8.2)
    d.arrow(60, 28, 68, 15, color=P["violet"], lw=1.8, style="<|-|>")
    d.arrow(91, 28, 83, 15, color=P["violet"], lw=1.8, style="<|-|>")
    d.text(59.5, 20, "DTLS ①\nA ↔ M", size=8, color=P["violet"], weight="bold")
    d.text(91.5, 20, "DTLS ②\nM' ↔ B", size=8, color=P["violet"], weight="bold")
    d.text(75.5, 6, "해시는 각자 일치 → 경고 없이 평문 열람", size=8, color=P["dim"])


diagram("10-mitm", draw, w=13.5, h=6.4, ymax=50)

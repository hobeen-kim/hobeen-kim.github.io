"""CH10 §2 SDP 교환 → ICE → DTLS 핸드셰이크 → SRTP 시퀀스 — (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    xb, xs, xd = 12, 50, 88

    actors = [
        (xb, "운영자 브라우저", "offerer · passive → DTLS 서버", P["blue"]),
        (xs, "시그널링 서버", "WSS", P["brown"]),
        (xd, "디바이스", "answerer · active → DTLS 클라이언트", P["green"]),
    ]
    for x, name, sub, fc in actors:
        d.box(x - 11, 61, 22, 7, fc)
        d.text(x, 65.6, name, size=10, weight="bold")
        d.text(x, 62.7, sub, size=7.5, color=P["dim"])
        y_end = 46 if x == xs else 6
        d.ax.plot([x, x], [y_end, 61], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", size=8):
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        d.text((x1 + x2) / 2, y + 1.3, label, size=size, color=color)

    # 시그널링 (SDP)
    hop(xb, xs, 56.5, "offer: a=setup:actpass, a=fingerprint A", P["orange"], size=7.6)
    hop(xs, xd, 54, "offer 전달", P["orange"], size=7.6)
    hop(xd, xs, 50, "answer: a=setup:active, a=fingerprint B", P["orange"], size=7.6)
    hop(xs, xb, 47.5, "answer 전달", P["orange"], size=7.6)

    # ICE
    d.arrow(xb, 43, xd, 43, color=P["violet"], style="<|-|>")
    d.text(xs, 44.4, "ICE 연결성 검사 (STUN Binding) — 후보 쌍 선택", size=8, color=P["violet"])

    # DTLS 1.2 핸드셰이크
    hop(xd, xb, 38.5, "ClientHello (use_srtp: 지원 프로파일 목록)", P["accent"])
    hop(xb, xd, 34, "ServerHello (프로파일 1개 선택), Certificate, CertificateRequest, …", P["accent"])
    hop(xd, xb, 29.5, "Certificate, ClientKeyExchange, CertificateVerify, Finished", P["accent"])
    hop(xb, xd, 25, "ChangeCipherSpec, Finished", P["accent"])

    # 검증 / 키 도출 노트
    for x in (xb, xd):
        d.box(x - 11, 15.5, 22, 6.5, P["chip"], ec=P["accent"], lw=1.1)
    d.text(xb, 18.75, "B 인증서 해시\n== answer의 fingerprint?", size=7.6)
    d.text(xd, 18.75, "A 인증서 해시\n== offer의 fingerprint?", size=7.6)
    d.text(xs, 18.75, "exporter\n\"EXTRACTOR-dtls_srtp\"\n→ SRTP 키", size=7.6, color=P["dim"])

    # 미디어
    d.arrow(xb, 9, xd, 9, color=P["accent"], lw=2.4, style="<|-|>")
    d.text(xs, 10.6, "SRTP/SRTCP 미디어 + DTLS 위 SCTP(DataChannel)", size=8.5,
           color=P["accent"], weight="bold")

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.4, label="시그널링(SDP)"),
        Line2D([0], [0], color=P["violet"], lw=2.4, label="STUN"),
        Line2D([0], [0], color=P["accent"], lw=2.4, label="DTLS · SRTP (같은 5-tuple)"),
    ], anchor=(0.4, 0.0), fontsize=7.5)


diagram("10-dtls-handshake", draw, w=13, h=8.2, ymax=69)

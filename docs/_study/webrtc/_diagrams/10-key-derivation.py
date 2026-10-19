"""CH10 §3 DTLS-SRTP exporter 키 도출 (AES_CM_128_HMAC_SHA1_80 기준) — (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # DTLS 세션
    d.box(2, 34, 22, 10, P["brown"])
    d.text(13, 40.6, "DTLS 핸드셰이크", size=10.5, weight="bold")
    d.text(13, 36.8, "(master secret)", size=8.5, color=P["dim"])

    d.box(32, 34, 26, 10, P["purple"])
    d.text(45, 40.6, "TLS exporter", size=10.5, weight="bold")
    d.text(45, 36.8, "label \"EXTRACTOR-dtls_srtp\"", size=8.3, color=P["dim"])
    d.arrow(24, 39, 32, 39)

    d.text(79, 41.5, "2 × (키 16B + salt 14B) = 60 바이트", size=9, color=P["dim"])
    d.arrow(58, 39, 64, 30.5, color=P["edge"], lw=1.3)

    # 키 머티리얼 바 (16 | 16 | 14 | 14)
    segs = [
        ("client key", 16, P["green"]),
        ("server key", 16, P["blue"]),
        ("client salt", 14, P["green"]),
        ("server salt", 14, P["blue"]),
    ]
    x0, scale = 20, 1.0
    x = x0
    centers = {}
    for name, n, fc in segs:
        w = n * scale
        d.box(x, 23, w, 7, fc)
        d.text(x + w / 2, 27.6, name, size=9, weight="bold")
        d.text(x + w / 2, 24.8, f"{n}B", size=8, color=P["dim"])
        centers[name] = x + w / 2
        x += w + 0.6

    # SRTP 컨텍스트
    d.box(4, 3, 40, 11, P["green"])
    d.text(24, 10.4, "active(DTLS 클라이언트) → passive 방향", size=9.5, weight="bold")
    d.text(24, 6.4, "client key + client salt", size=8.5, color=P["dim"])
    d.box(56, 3, 40, 11, P["blue"])
    d.text(76, 10.4, "passive(DTLS 서버) → active 방향", size=9.5, weight="bold")
    d.text(76, 6.4, "server key + server salt", size=8.5, color=P["dim"])

    d.arrow(centers["client key"], 23, 20, 14, color=P["accent"], lw=1.4)
    d.arrow(centers["client salt"], 23, 30, 14, color=P["accent"], lw=1.4)
    d.arrow(centers["server key"], 23, 70, 14, color=P["orange"], lw=1.4)
    d.arrow(centers["server salt"], 23, 80, 14, color=P["orange"], lw=1.4)
    d.text(50, 8.5, "각 방향\nSRTP KDF\n(RFC 3711)", size=8.3, color=P["dim"])


diagram("10-key-derivation", draw, w=12, h=5.4, ymax=46)

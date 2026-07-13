"""CH20 실행 티어 — 인터프리터→JIT→프로파일 기반 AOT 하이브리드."""
from _common import diagram


def draw(d):
    P = d.P

    tiers = [
        ("인터프리터", "설치 직후·콜드 코드\nmterp 어셈블리 실행", P["blue"]),
        ("JIT 컴파일", "hot 메서드 감지\nJIT 코드 캐시 · OSR", P["green"]),
        ("프로파일 기록", "profman → /data/misc/profiles\nhot 메서드 목록 축적", P["brown"]),
        ("AOT (speed-profile)", "bg-dexopt(유휴/충전 시)\n프로파일 기반 사전 컴파일", P["purple"]),
    ]
    for i, (name, desc, fc) in enumerate(tiers):
        x = 3 + i * 24
        d.box(x, 16, 21, 18, fc)
        d.text(x + 10.5, 30.5, name, size=9.3, weight="bold",
               color=P["accent"])
        d.text(x + 10.5, 23.5, desc, size=7.7, color=P["dim"])
        if i < 3:
            d.arrow(x + 21, 25, x + 24, 25, color=P["orange"], lw=1.7)

    # 순환 화살표: AOT 후에도 새 hot 코드는 다시 JIT
    d.arrow(85, 16, 34, 12, color=P["violet"], lw=1.4, rad=0.18, ls="--")
    d.text(60, 8.5, "새 hot 코드는 다시 JIT → 프로파일 갱신 (반복)",
           size=7.8, color=P["violet"])

    d.text(50, 38, "compiler filter: verify → quicken → speed-profile → speed",
           size=8.2, color=P["dim"])


diagram("20-compile-tiers", draw, w=13, h=5.4, ymax=44)

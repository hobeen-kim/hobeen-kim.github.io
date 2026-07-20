"""CH01 Open-Agriculture 생태계 — AgIsoStack++를 둘러싼 프로젝트들 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(4, 4, 92, 42, P["gray"])
    d.text(50, 43.2, "Open-Agriculture (GitHub 조직)", size=11, weight="bold",
           color=P["accent"])

    # 중심
    d.box(33, 21, 34, 11, P["blue"], ec=P["accent"], lw=2.0)
    d.text(50, 28.4, "AgIsoStack++", size=13, weight="bold")
    d.text(50, 24.4, "C++ ISO 11783 / J1939 스택", size=9, color=P["dim"])

    sides = [
        (7, 34, "AgIsoVirtualTerminal", "PC용 VT 서버", P["green"]),
        (71, 34, "AgIsoDDOPGenerator", "DDOP 저작 도구", P["purple"]),
        (7, 8, "AgIsoStack-rs", "Rust 바인딩·포팅", P["brown"]),
        (71, 8, "예제·문서·튜토리얼", "examples / sphinx", P["chip"]),
    ]
    for x, y, name, sub, fc in sides:
        d.box(x, y, 22, 9, fc)
        d.text(x + 11, y + 6, name, size=9.5, weight="bold")
        d.text(x + 11, y + 2.6, sub, size=8, color=P["dim"])

    d.arrow(29, 38.5, 33, 31, color=P["accent"], lw=1.4, rad=0.15)
    d.arrow(71, 38.5, 67, 31, color=P["accent"], lw=1.4, rad=-0.15)
    d.arrow(29, 12.5, 33, 22, color=P["accent"], lw=1.4, rad=-0.15)
    d.arrow(71, 12.5, 67, 22, color=P["accent"], lw=1.4, rad=0.15)


diagram("01-ecosystem", draw, w=11, h=5.4, ymax=48)

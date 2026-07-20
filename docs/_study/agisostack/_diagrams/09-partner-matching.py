"""CH9 §1 NAME 필터 매칭 — 버스에 올라온 NAME 중 무엇이 파트너가 되는가."""
from _common import diagram


def draw(d):
    P = d.P

    # 필터 정의
    d.box(2, 24, 28, 14, P["blue"])
    d.text(16, 35, "std::vector<NAMEFilter>", size=10, weight="bold")
    d.text(16, 29.5, "NAMEParameters::FunctionCode\n== Function::VirtualTerminal",
           size=9.2, color=P["dim"])

    # 버스에 나타난 NAME들
    d.text(46, 40, "주소 클레임한 장치들", size=9.5, color=P["dim"])
    cands = [
        ("VT\nFunctionCode 29", P["green"], True),
        ("TaskController\nFunctionCode 130", P["gray"], False),
        ("SteeringControl\nFunctionCode 16", P["gray"], False),
    ]
    for i, (lb, fc, ok) in enumerate(cands):
        y = 28 - i * 12
        d.box(38, y, 24, 10, fc)
        d.text(50, y + 5, lb, size=9.2)
        d.arrow(30, 31, 38, y + 5,
                color=P["accent"] if ok else P["edge"],
                lw=1.6 if ok else 1.0,
                ls="-" if ok else "--")
        d.text(34, (31 + y + 5) / 2 + 1.2, "일치" if ok else "무시",
               size=8, color=P["accent"] if ok else P["dim"])

    # 파트너
    d.box(72, 22, 26, 12, P["purple"])
    d.text(85, 28, "PartneredControlFunction\n(myPartner)", size=9.8)
    d.arrow(62, 33, 72, 30, color=P["accent"])

    d.box(72, 6, 26, 9, P["chip"])
    d.text(85, 10.5, "send_can_message(..., myECU, myPartner)\n→ DA = 파트너의 클레임 주소",
           size=8.6, color=P["dim"])
    d.arrow(85, 22, 85, 15, color=P["edge"], style="-", lw=1.0)


diagram("09-partner-matching", draw, w=12.5, h=5.4, ymax=44)

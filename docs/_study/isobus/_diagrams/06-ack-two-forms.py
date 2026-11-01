"""CH06 §7 확인 응답의 두 형식: CAN 수준(ACK 슬롯·에러 프레임)과 응용 수준(PGN 59392) (light/dark PNG)."""
from _common import diagram

XS, XO, XD = 20, 52, 84     # 송신 CF, 다른 노드들, 목적지 CF


def draw(d):
    P = d.P
    top = 54
    # 묶음 상자를 먼저 그린다
    d.box(4, 27, 92, 24, P["gray"], ec=P["edge"])
    d.box(4, 5, 92, 19, P["purple"], ec=P["edge"], alpha=0.45)
    for x, name in ((XS, "송신 CF"), (XO, "다른 노드들"), (XD, "목적지 CF\n(DA)")):
        d.box(x - 8, top, 16, 5.4, P["blue"])
        d.text(x, top + 2.7, name, size=9.4)
        d.ax.plot([x, x], [3, top], color=P["edge"], lw=1.2)

    d.text(22, 48.6, "CAN 계층 (컨트롤러 하드웨어)", size=8.8, color=P["dim"], ha="left")
    d.arrow(XS, 45, XD, 42.5)
    d.text(36, 45.6, "데이터 프레임 (DA = 목적지)", size=8.6)
    d.arrow(XO, 38.5, XS, 37, color=P["violet"])
    d.text(36, 39.9, "ACK 슬롯 dominant", size=8.2, color=P["violet"])
    d.text(36, 34.9, "적어도 한 노드 수신", size=7.8, color=P["dim"])
    d.text(68, 31.2, "에러 프레임 없음 = 켜진 노드 모두 정상 수신", size=8.2, color=P["dim"])

    d.text(22, 21.6, "응용 계층 (PGN 59392)", size=8.8, color=P["dim"], ha="left")
    d.arrow(XD, 17, XS, 13, color=P["accent"])
    d.text(68, 19.2, "ACK / NACK /\nAccess Denied / Cannot Respond", size=8.2)
    d.ax.plot([XD + 2.5, XD + 2.5], [42.5, 17], color=P["violet"], lw=1.2)
    d.text(XD + 3.5, 30, "Tr ≤ 200 ms", size=8, color=P["violet"], ha="left")
    d.ax.plot([XS - 2.5, XS - 2.5], [45, 8], color=P["orange"], lw=1.4)
    for yy in (45, 8):
        d.ax.plot([XS - 3.3, XS - 1.7], [yy, yy], color=P["orange"], lw=1.4)
    d.text(XS - 3.5, 10.5, "T3 1.25 s 동안\n응답 대기", size=8, color=P["orange"], ha="right")


diagram("06-ack-two-forms", draw, w=11, h=5.8, xmax=100, ymax=61)

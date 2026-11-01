"""CH10 §5 엔진을 예로 든 세 장면: 특정 요청, 전역 요청, 명령과 ACK·NACK (light/dark PNG)."""
from _common import diagram

REQ, ENG, CMD = 26, 58, 90


def draw(d):
    P = d.P
    top = 66
    for x, label, color in ((REQ, "요청자\nSA 0x03", "blue"),
                            (ENG, "엔진\nSA 0x00", "green"),
                            (CMD, "명령자\nSA 0xF0", "purple")):
        d.box(x - 9, top, 18, 7, P[color])
        d.text(x, top + 3.5, label, size=9.0)
        d.ax.plot([x, x], [11, top], color=P["edge"], lw=1.0, ls=(0, (2, 3)))

    def msg(x1, x2, y, dashed=False):
        d.arrow(x1, y, x2, y, color=P["dim"] if dashed else P["accent"],
                ls="--" if dashed else "-", lw=1.6)

    def lab(x, y, s, dashed=False):
        d.text(x, y, s, size=8.2, color=P["dim"] if dashed else P["text"])

    def scene(y, s):
        d.text(1, y, s, size=9.0, color=P["dim"], ha="left")

    scene(56, "특정\n요청")
    msg(REQ, ENG, 58)
    lab((REQ + ENG) / 2, 60.8, "특정 요청 0x18EA0003\nEB FE 00 (PGN 65259)")
    msg(ENG, REQ, 50, dashed=True)
    lab((REQ + ENG) / 2, 52.8, "데이터(길면 RTS/CTS)\n또는 NACK 0x18E80300", dashed=True)

    scene(38, "전역\n요청")
    msg(REQ, ENG, 41)
    msg(REQ, CMD, 39)
    lab((REQ + ENG) / 2, 43.8, "전역 요청 0x18EAFF03\nEB FE 00")
    msg(ENG, REQ, 32, dashed=True)
    msg(ENG, CMD, 30, dashed=True)
    lab((REQ + ENG) / 2, 34.8, "모두에게 응답(길면 BAM)\n미지원이면 침묵", dashed=True)

    scene(20, "명령")
    msg(CMD, ENG, 23)
    lab((ENG + CMD) / 2, 25.6, "명령(어떤 명령 PGN)")
    msg(ENG, CMD, 15, dashed=True)
    lab((ENG + CMD) / 2, 17.8, "ACK 또는 NACK\n0x18E8F000", dashed=True)


diagram("10-request-ack-scenes", draw, w=10.5, h=6.4, xmax=100, ymax=74)

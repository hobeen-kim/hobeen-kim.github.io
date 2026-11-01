"""54장 3절: Byte 3에 실행 상태와 State ID를 함께 담는 비트 배치 (예: 0x42, light/dark PNG)."""
from _common import diagram

BITS = [0, 1, 0, 0, 0, 0, 1, 0]  # Bit 8 .. Bit 1 of 0x42
X0, CW = 14, 7


def draw(d):
    P = d.P

    d.text(7, 24, "0x42", size=12, weight="bold")
    for i, b in enumerate(BITS):
        x = X0 + i * CW
        d.box(x, 20, CW, 8, P["brown"] if i < 2 else P["blue"], r=0.01)
        d.text(x + CW / 2, 24, str(b), size=12, weight="bold")
        d.text(x + CW / 2, 30.6, f"Bit {8 - i}", size=8.5, color=P["dim"])

    def bracket(x1, x2, label):
        d.ax.plot([x1 + 0.4, x1 + 0.4, x2 - 0.4, x2 - 0.4], [18.6, 17.4, 17.4, 18.6],
                  color=P["edge"], lw=1.3)
        d.text((x1 + x2) / 2, 12.4, label, size=9)

    bracket(X0, X0 + 2 * CW, "실행 상태 (Bits 7-8)\n01 = 시작")
    bracket(X0 + 2 * CW, X0 + 8 * CW, "State ID (Bits 1-6)\n000010 = 2")

    d.box(75, 7, 23, 26, P["chip"])
    d.text(77, 29.6, "실행 상태 값", size=9, weight="bold", ha="left")
    for k, line in enumerate(["00  시작·완료 동시", "01  시작", "10  완료", "11  실행 중 오류"]):
        d.text(77, 24.6 - k * 4.6, line, size=9, ha="left")


diagram("54-byte3-bits", draw, w=12, h=4.4, xmax=100, ymax=36)

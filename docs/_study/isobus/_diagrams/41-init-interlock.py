"""41장 TC 초기화 5단계와 클라이언트 초기화 9단계가 맞물리는 순서 (light/dark PNG)."""
from _common import diagram

X0, CW, GAP = 10.5, 9.9, 0.6
TC_Y, TC_H = 29, 9
CL_Y, CL_H = 5, 11


def col_x(c):
    return X0 + c * CW


def box(d, c0, c1, y, h, label, color, size=8.4):
    x = col_x(c0)
    w = (c1 - c0 + 1) * CW - GAP
    d.box(x, y, w, h, d.P[color])
    d.text(x + w / 2, y + h / 2, label, size=size)


def draw(d):
    P = d.P
    d.text(5, TC_Y + TC_H / 2, "TC", size=11, weight="bold")
    d.text(5, CL_Y + CL_H / 2, "클라이언트", size=10, weight="bold")

    box(d, 0, 0, TC_Y, TC_H, "1. 주소 클레임\n+ 전역 요청", "green")
    box(d, 1, 1, TC_Y, TC_H, "2. 6초 대기", "green")
    box(d, 2, 2, TC_Y, TC_H, "3. TC Status\n송신 시작", "green")
    box(d, 3, 9, 41, 4.6, "4. 클라이언트의 DDOP 업로드·초기화 허용 (이후 계속)", "green")
    box(d, 5, 6, TC_Y, TC_H, "5. 클라이언트\n버전 묻기 (v4)", "green")

    box(d, 0, 1, CL_Y, CL_H, "1. 주소 클레임 후\n6초 대기", "blue")
    labels = ["2. TC Status\n기다리기", "3. WSM으로\n자기소개", "4. Client Task\n송신 시작",
              "5. TC 버전\n묻기 (v4)", "6. TC 질문에\n답하기 (v4)", "7. 언어·형식\n요청 (선택)",
              "8. 내 DDOP\n있는지 묻기", "9. 활성화\n(없으면\n전송 후)"]
    for i, label in enumerate(labels):
        box(d, i + 2, i + 2, CL_Y, CL_H, label, "blue")

    def cx(c):
        return col_x(c) + (CW - GAP) / 2

    d.arrow(cx(2), TC_Y - 0.2, cx(2), CL_Y + CL_H + 0.2)
    d.text(cx(2) + 1.2, 22.5, "TC Status", size=8.4, color=P["accent"], ha="left")

    d.arrow(cx(5), CL_Y + CL_H + 0.2, cx(5), TC_Y - 0.2)
    d.text(cx(5) - 1.2, 22.5, "Request\nVersion", size=8.4, color=P["accent"], ha="right")
    d.arrow(cx(6), TC_Y - 0.2, cx(6), CL_Y + CL_H + 0.2)
    d.text(cx(6) + 1.2, 22.5, "Request\nVersion", size=8.4, color=P["accent"], ha="left")

    top = CL_Y + CL_H + 1.4
    d.ax.plot([col_x(8), col_x(9) + CW - GAP], [top, top], color=P["violet"], lw=1.6, zorder=4)
    for x in (col_x(8), col_x(9) + CW - GAP):
        d.ax.plot([x, x], [top, top - 0.9], color=P["violet"], lw=1.6, zorder=4)
    xb = col_x(9) - GAP / 2
    d.arrow(xb, 40.8, xb, top + 0.1, color=P["violet"], ls="--")
    d.text(xb - 1.2, 30.5, "8~9단계를\n받아 준다", size=8.4, color=P["violet"], ha="right")

    d.arrow(X0, 1.6, 108, 1.6, color=P["dim"], lw=1.1)
    d.text(106, 3.3, "시간", size=8.4, color=P["dim"], ha="right")


diagram("41-init-interlock", draw, w=13, h=5.9, xmax=110, ymax=50)

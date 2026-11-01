"""CH7 5절 64바이트 전송 시간 비교: Classic CAN 8프레임(2048 µs)과 CAN FD 1프레임(361 µs) (light/dark PNG)."""
from _common import diagram

X0, SCALE = 22, 70 / 2048
CLASSIC_FRAME_US, N_FRAMES = 256, 8
FD_PARTS = [("중재", 72, "gray"), ("데이터", 269, "blue"), ("복귀", 20, "gray")]
Y_C, Y_F, H = 26, 10, 8


def draw(d):
    P = d.P
    ax = d.ax

    d.text(2, Y_C + H / 2 + 1.4, "Classic CAN", size=10, weight="bold", ha="left")
    d.text(2, Y_C + H / 2 - 1.8, "500 kbps, 8프레임", size=8.4, color=P["dim"], ha="left")
    for i in range(N_FRAMES):
        x = X0 + i * CLASSIC_FRAME_US * SCALE
        d.box(x, Y_C, CLASSIC_FRAME_US * SCALE - 0.4, H, P["brown"], lw=1.0, r=0.01)
        d.text(x + CLASSIC_FRAME_US * SCALE / 2, Y_C + H / 2, f"{i + 1}", size=9)
    d.text(X0 + 2048 * SCALE + 1.2, Y_C + H / 2, "2048 $\\mu$s", size=9.6, weight="bold", ha="left")

    d.text(2, Y_F + H / 2 + 1.4, "CAN FD", size=10, weight="bold", ha="left")
    d.text(2, Y_F + H / 2 - 1.8, "500 kbps + 2 Mbps, 1프레임", size=8.4, color=P["dim"], ha="left")
    x = X0
    for name, us, color in FD_PARTS:
        w = us * SCALE
        d.box(x, Y_F, w, H, P[color], ec=P["accent"] if color == "blue" else P["edge"], lw=1.2, r=0.01)
        x += w
    d.text(x + 1.2, Y_F + H / 2, "361 $\\mu$s", size=9.6, weight="bold", ha="left", color=P["accent"])
    d.text(X0, Y_F - 3.0, "중재 72 $\\mu$s + 데이터 269 $\\mu$s + 복귀 20 $\\mu$s", size=8.4, color=P["dim"], ha="left")

    for t in (0, 500, 1000, 1500, 2000):
        xt = X0 + t * SCALE
        ax.plot([xt, xt], [Y_C + H + 1.2, Y_C + H + 2.4], color=P["edge"], lw=1.0)
        d.text(xt, Y_C + H + 4.0, f"{t} $\\mu$s", size=8, color=P["dim"])
    ax.plot([X0, X0 + 2048 * SCALE], [Y_C + H + 1.2, Y_C + H + 1.2], color=P["edge"], lw=1.0)


diagram("07-64byte-time-compare", draw, w=12, h=3.8, xmax=100, ymax=40)

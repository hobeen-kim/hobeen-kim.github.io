"""CH11 §8 RTS/CTS 세션 상태 머신: 송신 측·수신 측 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def state(x, y, w, h, label, fc=None):
        d.box(x, y, w, h, fc or P["gray"])
        d.text(x + w / 2, y + h / 2, label, size=9.4)

    def lab(x, y, s, color=None, ha="center"):
        d.text(x, y, s, size=8.3, color=color or P["dim"], ha=ha)

    # ---------------- 송신 측 (위) ----------------
    d.text(2, 58, "송신 측 (RTS를 보낸 CF)", size=10.5, weight="bold", ha="left")
    state(2, 44, 11, 7, "IDLE")
    state(22, 44, 17, 7, "CTS 대기\nT3 1250 ms", P["blue"])
    state(50, 44, 18, 7, "데이터 송신\nDT 간격 ≤ 200 ms", P["blue"])
    state(50, 31, 18, 7, "HOLD\nT4 1050 ms", P["brown"])
    state(84, 44, 13, 7, "닫힘", P["green"])

    d.arrow(13, 47.5, 22, 47.5)
    lab(17.5, 49.5, "RTS 송신")
    d.arrow(39, 48.8, 50, 48.8)
    lab(44.5, 50.6, "CTS(n>0)")
    d.arrow(50, 46.2, 39, 46.2, color=P["violet"])
    lab(44.5, 44.4, "묶음 끝", P["violet"])
    d.arrow(32, 44, 52, 38, color=P["orange"], rad=0.15)
    lab(37, 38.6, "CTS(0)", P["orange"])
    d.arrow(64, 38, 64, 44)
    lab(66, 41, "CTS(n>0)", ha="left")
    d.arrow(68, 49.5, 84, 49.5)
    lab(76, 51.4, "EoMA 수신")
    lab(90.5, 38.5, "모든 상태에서\nAbort 송수신 시 닫힘\n타임아웃이면 Abort 3")

    # ---------------- 수신 측 (아래) ----------------
    d.text(2, 27.5, "수신 측 (CTS를 보내는 CF)", size=10.5, weight="bold", ha="left")
    state(2, 12, 11, 7, "IDLE")
    state(22, 12, 15, 7, "RTS 검토\n자원 판단", P["purple"])
    state(48, 12, 20, 7, "데이터 수신\nT2(첫 DT)·T1(다음 DT)", P["blue"])
    state(48, 1, 20, 6.5, "HOLD 유지\nTh ≤ 500 ms마다 CTS(0)", P["brown"])
    state(84, 12, 13, 7, "닫힘", P["green"])

    d.arrow(13, 15.5, 22, 15.5)
    lab(17.5, 17.4, "RTS 수신")
    d.arrow(37, 16.8, 48, 16.8)
    lab(42.5, 18.6, "CTS 송신\n= 연결 성립")

    # 거절 경로: RTS 검토 -> 닫힘
    d.ax.plot([29.5, 29.5, 88], [19, 23.5, 23.5], color=P["dim"], lw=1.6)
    d.arrow(88, 23.5, 88, 19, color=P["dim"])
    lab(75, 24.9, "거절: Abort(1·2)")

    # 자기 루프: 다음 묶음·재전송 CTS
    d.arrow(65, 19, 51, 19, color=P["violet"], rad=0.35)
    lab(58, 22.4, "다음·재전송 CTS", P["violet"])

    d.arrow(68, 16.8, 84, 16.8)
    lab(76, 18.6, "전부 수신\nEoMA 송신")
    d.arrow(68, 13.6, 84, 13.6, color=P["dim"], ls="--")
    lab(76, 11.6, "T1·T2 만료\nAbort 3", P["dim"])
    d.arrow(53, 12, 53, 7.5, color=P["orange"])
    lab(51.5, 9.8, "CTS(0)", P["orange"], ha="right")
    d.arrow(63, 7.5, 63, 12)
    lab(64.5, 9.8, "CTS(n)", ha="left")


diagram("11-tp-session-state", draw, w=12.5, h=7, xmax=100, ymax=60)

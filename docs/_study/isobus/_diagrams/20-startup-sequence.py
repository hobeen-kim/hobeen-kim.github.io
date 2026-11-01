"""20장 4절: 시동 뒤 ISOBUS 통신이 자리 잡는 메시지 흐름 (light/dark PNG)."""
from _common import diagram

X = {"TECU": 12, "WSM": 38, "VT": 64, "TC": 88}
TOP = 100
STEP = 5.2


def row(i):
    return TOP - 6 - i * STEP


def message(d, i, a, b, label, ls="-", lw=1.7):
    y = row(i)
    d.arrow(X[a], y, X[b], y, ls=ls, lw=lw)
    d.ax.text((X[a] + X[b]) / 2, y + 1.6, label, fontsize=8.8, color=d.P["text"],
              ha="center", va="center", zorder=5,
              bbox=dict(facecolor=d.P["bg"], edgecolor="none", pad=1.2))


def band(d, i, label):
    y = row(i)
    d.box(3, y - 1.9, 94, 3.8, d.P["chip"], ec=d.P["accent"], lw=1.1)
    d.text(50, y, label, size=9, color=d.P["accent"], weight="bold")


def draw(d):
    P = d.P
    for name, x in X.items():
        label = {"TECU": "TECU", "WSM": "WSM\n(Working Set Master)",
                 "VT": "VT", "TC": "TC"}[name]
        d.box(x - 10, TOP, 20, 6.5, P["blue"])
        d.text(x, TOP + 3.25, label, size=9.5, weight="bold")
        d.ax.plot([x, x], [1.5, TOP], color=P["edge"], lw=1.0, ls="--", zorder=1)

    band(d, 0, "전원 ON / 시동")
    y = row(1)
    for x in X.values():
        d.box(x - 7, y - 1.6, 14, 3.2, P["brown"])
        d.text(x, y, "주소 클레임", size=8.6)
    band(d, 2, "약 250 ms: 모든 ECU 주소 확정")

    message(d, 3, "VT", "WSM", "VT Status (1초 주기 브로드캐스트, WSM은 이것을 먼저 기다린다)", ls="--")
    message(d, 4, "WSM", "TC", "Working Set Master (PGN 65037, 브로드캐스트)")
    message(d, 5, "WSM", "TC", "Working Set Member (PGN 65036, 멤버 수-1개)")
    band(d, 6, "약 1 s: Working Set 구성 완료")

    message(d, 7, "WSM", "VT", "Working Set Maintenance 시작 (1초 주기, 첫 메시지만 initiating)")
    message(d, 8, "WSM", "VT", "오브젝트 풀 전송 시작 (작업기 UI 데이터)", lw=2.6)
    message(d, 9, "VT", "WSM", "오브젝트 풀 수신 완료", ls="--")
    message(d, 10, "WSM", "VT", "End of Object Pool")
    message(d, 11, "VT", "WSM", "End of Object Pool 응답", ls="--")
    message(d, 12, "WSM", "TC", "Device Descriptor 전송 (작업 장치 구조 정보)", lw=2.6)
    message(d, 13, "TC", "WSM", "Device Descriptor 수신 완료", ls="--")
    band(d, 14, "정상 동작: VT에 작업기 화면 표시, TC 작업 시작 가능")

    message(d, 15, "TECU", "WSM", "속도·PTO·히치 정보 (주기 전송)")
    message(d, 16, "TC", "WSM", "섹션 제어 명령")
    message(d, 17, "WSM", "VT", "화면 업데이트 (작업기 상태)")


diagram("20-startup-sequence", draw, w=12, h=11.5, xmax=100, ymax=108)

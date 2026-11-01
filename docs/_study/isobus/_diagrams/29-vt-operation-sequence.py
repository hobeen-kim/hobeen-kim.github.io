"""CH29 VT 동작 순서: 연결 확인, 오브젝트 풀 전송과 표시, 운전자 입력과 갱신 (light/dark PNG)."""
from _common import diagram

ECU, VT, USER = 21, 57, 89
TOP = 78


def draw(d):
    P = d.P
    for x, name, col, w in [(ECU, "작업기 ECU\n(VT Client)", P["green"], 20),
                            (VT, "VT Server\n(디스플레이)", P["blue"], 20),
                            (USER, "운전자", P["brown"], 14)]:
        d.box(x - w / 2, TOP, w, 6.6, col)
        d.text(x, TOP + 3.3, name, size=10, weight="bold")
        d.ax.plot([x, x], [8, TOP], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=1.6)
        d.text((x1 + x2) / 2, y + 1.3, label, size=8.6, color=color)

    def self_box(x, y, w, label):
        d.box(x - w / 2, y - 1.8, w, 3.6, P["purple"], lw=1.1)
        d.text(x, y, label, size=8.6)

    per, cmd, rsp, op = P["violet"], P["accent"], P["dim"], P["orange"]
    hop(VT, ECU, 72.5, "VT Status (1초 주기 브로드캐스트)", per)
    hop(ECU, VT, 67.5, "Working Set Maintenance 전송 시작 (1초 주기)", per)
    hop(ECU, VT, 62.5, "Get Memory 등 기술 데이터 요청", cmd)
    hop(VT, ECU, 58.0, "응답 (VT 버전, 메모리 상태 등)", rsp, ls="--")

    hop(ECU, VT, 50.5, "Object Pool Transfer (화면 정의 데이터 전송)", cmd)
    hop(ECU, VT, 46.0, "End of Object Pool (전송 완료 통지)", cmd)
    self_box(VT, 41.5, 30, "오브젝트 풀 파싱 및 화면 렌더링")
    hop(VT, ECU, 37.0, "End of Object Pool Response (오류 여부 보고)", rsp, ls="--")

    hop(USER, VT, 29.5, "버튼 클릭 / 소프트키 입력", op)
    hop(VT, ECU, 25.0, "Button Activation Message (입력 이벤트 전달)", cmd)
    self_box(ECU, 20.5, 24, "입력 처리 (예: 살포량 변경)")
    hop(ECU, VT, 15.5, "Change Numeric Value (화면 데이터 갱신)", cmd)
    hop(VT, USER, 11.0, "새로운 값 화면 표시", op)

    for y1, y2, label in [(55.0, 76.0, "연결 확인"), (34.0, 54.0, "풀 전송·표시"),
                          (8.5, 33.0, "입력과 갱신")]:
        d.ax.plot([5.2, 5.2], [y1, y2], color=P["edge"], lw=1.6, zorder=2)
        d.ax.plot([5.2, 6.4], [y1, y1], color=P["edge"], lw=1.6, zorder=2)
        d.ax.plot([5.2, 6.4], [y2, y2], color=P["edge"], lw=1.6, zorder=2)
        d.ax.text(3.0, (y1 + y2) / 2, label, rotation=90, fontsize=9.5,
                  color=P["dim"], ha="center", va="center", zorder=5)

    lx, ly = 30, 3.2
    for i, (color, ls, label) in enumerate([(per, "-", "주기 메시지"), (cmd, "-", "명령·요청"),
                                            (rsp, "--", "응답"), (op, "-", "운전자 조작·표시")]):
        x = lx + i * 17
        d.arrow(x, ly, x + 4.5, ly, color=color, ls=ls, lw=1.6)
        d.text(x + 5.5, ly, label, size=8.4, color=P["dim"], ha="left")


diagram("29-vt-operation-sequence", draw, w=13, h=10.4, xmax=100, ymax=86)

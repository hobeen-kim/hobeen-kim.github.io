"""20장 3절: ISOBUS 위 ECU들의 역할과 주로 오가는 정보 (light/dark PNG)."""
from _common import diagram

W, H = 27, 13

NODES = {
    # 이름: (x0, y0, 제목, 설명, 색 키)
    "AUX": (4, 64, "AUX Input Device", "조이스틱, 버튼 패드\n운전자 추가 조작 입력\nAUX-N / AUX-O 기능", "gray"),
    "GPS": (36.5, 64, "GPS Receiver", "위치 정보 (위도·경도)\nNMEA 0183 / ISOBUS PGN\n정밀 농업 기반 데이터", "gray"),
    "VT": (4, 43, "VT (Virtual Terminal)", "트랙터 캐빈의 디스플레이\n작업기 UI를 화면에 표시\n운전자 조작 입력 처리", "blue"),
    "TC": (36.5, 43, "TC (Task Controller)", "작업 계획(Task) 관리\n섹션 제어, 처방도 적용\n작업 데이터 기록 (ISOXML)", "blue"),
    "TECU": (69, 43, "TECU (Tractor ECU)", "트랙터 정보 브로드캐스트\n속도, PTO RPM, 히치 위치\n엔진 RPM, 연료량 등", "blue"),
    "WSM": (36.5, 22, "Working Set Master", "작업기 대표 ECU\n작업기 내 ECU 통합 관리\nVT·TC와 협상", "green"),
    "MEM": (36.5, 1, "Working Set Member", "작업기 내 개별 ECU\n섹션 밸브, 센서, 모터 등\nMaster 지시에 따라 동작", "green"),
}


def node(d, key):
    P = d.P
    x, y, title, body, fc = NODES[key]
    d.box(x, y, W, H, P[fc])
    d.text(x + W / 2, y + H - 2.6, title, size=10, weight="bold")
    d.text(x + W / 2, y + 4.6, body, size=8.6, color=P["dim"])


def link(d, p1, p2, label, lx, ly, ha="center"):
    d.arrow(p1[0], p1[1], p2[0], p2[1], ls="--", lw=1.6)
    d.text(lx, ly, label, size=9, color=d.P["accent"], ha=ha)


def draw(d):
    for key in NODES:
        node(d, key)
    link(d, (17.5, 64), (17.5, 56), "조작 신호", 19, 60, ha="left")
    link(d, (50, 64), (50, 56), "위치 정보", 51.5, 60, ha="left")
    link(d, (17.5, 43), (40, 35), "UI 요청/응답", 26.5, 37.5, ha="right")
    link(d, (50, 43), (50, 35), "작업 명령", 51.5, 39, ha="left")
    link(d, (82.5, 43), (60, 35), "속도·PTO 정보", 72.5, 37.5, ha="left")
    link(d, (50, 22), (50, 14), "내부 제어", 51.5, 18, ha="left")


diagram("20-ecu-roles", draw, w=12, h=8.6, xmax=100, ymax=78)

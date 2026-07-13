"""CH21 libbinder 클래스 관계 — IInterface/IBinder 계층과 프로세스 상태 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 서버 측 (Bn)
    d.box(3, 6, 44, 36, P["gray"], ec=P["accent"], lw=1.5)
    d.text(25, 39, "서버 프로세스", size=10, weight="bold", color=P["accent"])
    d.box(6, 31, 38, 5.5, P["green"])
    d.text(25, 33.75, "IInterface  (인터페이스 계약)", size=8.8)
    d.box(6, 24, 38, 5.5, P["green"])
    d.text(25, 26.75, "BnInterface<ICanAccessService>", size=8.8)
    d.box(6, 17, 38, 5.5, P["green"])
    d.text(25, 19.75, "BBinder  (onTransact 수신)", size=8.8)
    d.box(6, 9, 38, 6, P["blue"])
    d.text(25, 12, "IPCThreadState  ·  ProcessState\n(/dev/binder mmap · 스레드풀)", size=8)

    # 클라이언트 측 (Bp)
    d.box(53, 6, 44, 36, P["gray"], ec=P["accent"], lw=1.5)
    d.text(75, 39, "클라이언트 프로세스", size=10, weight="bold", color=P["accent"])
    d.box(56, 31, 38, 5.5, P["brown"])
    d.text(75, 33.75, "IInterface  (동일 계약)", size=8.8)
    d.box(56, 24, 38, 5.5, P["brown"])
    d.text(75, 26.75, "BpInterface<ICanAccessService>", size=8.8)
    d.box(56, 17, 38, 5.5, P["brown"])
    d.text(75, 19.75, "BpBinder  (transact 송신 · 핸들)", size=8.8)
    d.box(56, 9, 38, 6, P["blue"])
    d.text(75, 12, "IPCThreadState  ·  ProcessState", size=8)

    # sp<> 스마트 포인터 표시
    d.text(25, 5.2, "sp<> / wp<>  ·  RefBase 참조 카운팅", size=8, color=P["dim"])
    d.text(75, 5.2, "sp<> / wp<>  ·  RefBase 참조 카운팅", size=8, color=P["dim"])

    # transact 화살표 (커널 경유)
    d.arrow(47, 20, 53, 20, color=P["orange"], rad=0.0)
    d.arrow(53, 18, 47, 18, color=P["violet"], rad=0.0)
    d.text(50, 22.5, "transact", size=8, color=P["orange"])
    d.text(50, 15.5, "reply", size=8, color=P["violet"])
    d.text(50, 30, "커널\nbinder\n드라이버", size=8, color=P["dim"])


diagram("21-libbinder-classes", draw, w=13, h=6.0, xmax=100, ymax=44)

"""CH22 트랜잭션 커널 경로 — one-copy 메커니즘 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 송신 프로세스
    d.box(3, 22, 26, 18, P["gray"], ec=P["accent"], lw=1.5)
    d.text(16, 37, "송신 프로세스 A", size=9.5, weight="bold", color=P["accent"])
    d.box(6, 30, 20, 5, P["brown"])
    d.text(16, 32.5, "Parcel (유저 버퍼)", size=8.3)
    d.box(6, 23.5, 20, 4.5, P["blue"])
    d.text(16, 25.75, "ioctl BINDER_WRITE_READ", size=7.8)

    # 커널 드라이버
    d.box(35, 8, 30, 34, P["gray"], ec=P["accent"], lw=1.7)
    d.text(50, 39, "binder 드라이버", size=9.5, weight="bold", color=P["accent"])
    d.box(38, 30, 24, 5, P["purple"])
    d.text(50, 32.5, "대상 노드 조회\n(handle → binder_node)", size=7.6)
    d.box(38, 22, 24, 5, P["purple"])
    d.text(50, 24.5, "수신자 mmap 버퍼에\n1회 copy_from_user", size=7.6)
    d.box(38, 14, 24, 5, P["purple"])
    d.text(50, 16.5, "대상 스레드 todo 큐에\n트랜잭션 큐잉", size=7.6)

    # 수신 프로세스
    d.box(71, 22, 26, 18, P["gray"], ec=P["accent"], lw=1.5)
    d.text(84, 37, "수신 프로세스 B", size=9.5, weight="bold", color=P["accent"])
    d.box(74, 30, 20, 5, P["green"])
    d.text(84, 32.5, "mmap 수신 버퍼\n(읽기 전용 매핑)", size=7.6)
    d.box(74, 23.5, 20, 4.5, P["blue"])
    d.text(84, 25.75, "BR_TRANSACTION 처리", size=7.6)

    # 화살표
    d.arrow(29, 26, 35, 26, color=P["orange"])
    d.arrow(62, 32.5, 71, 32.5, color=P["orange"], rad=-0.1)
    d.text(66, 35.5, "포인터만 전달", size=7.5, color=P["orange"])

    # one-copy 강조
    d.text(50, 11, "복사는 A→커널 매핑 1회뿐\n= one-copy", size=8, color=P["orange"], weight="bold")
    d.text(50, 5, "1MB - 8KB 트랜잭션 버퍼 한계 초과 시 TransactionTooLargeException",
           size=8, color=P["dim"])


diagram("22-transaction-flow", draw, w=13, h=5.8, xmax=100, ymax=43)

"""CH22 드라이버 자료구조 — binder_proc/node/ref/thread 관계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 서버 프로세스 측
    d.box(3, 6, 40, 34, P["gray"], ec=P["accent"], lw=1.5)
    d.text(23, 37, "서버 binder_proc", size=9.5, weight="bold", color=P["accent"])
    d.box(7, 28, 32, 6, P["green"])
    d.text(23, 31, "binder_node\n(서비스 실체 · 소유자)", size=8)
    d.box(7, 18, 15, 6, P["blue"])
    d.text(14.5, 21, "binder_thread\n#1", size=7.8)
    d.box(24, 18, 15, 6, P["blue"])
    d.text(31.5, 21, "binder_thread\n#2", size=7.8)
    d.text(23, 11, "todo 큐 · 스레드풀\n(BR_SPAWN_LOOPER로 확장)", size=7.8, color=P["dim"])

    # 클라이언트 프로세스 측
    d.box(57, 6, 40, 34, P["gray"], ec=P["accent"], lw=1.5)
    d.text(77, 37, "클라이언트 binder_proc", size=9.5, weight="bold", color=P["accent"])
    d.box(61, 28, 32, 6, P["brown"])
    d.text(77, 31, "binder_ref\n(node를 가리키는 핸들)", size=8)
    d.box(61, 18, 32, 6, P["blue"])
    d.text(77, 21, "handle 정수 → binder_ref", size=8)
    d.text(77, 12, "유저스페이스는 handle만 안다\n(커널이 node로 변환)", size=7.8, color=P["dim"])

    # 참조 화살표
    d.arrow(61, 31, 39, 31, color=P["orange"], rad=0.15)
    d.text(50, 35, "ref → node\n신원 보증", size=7.5, color=P["orange"])
    d.text(50, 22, "커널만\nnode 포인터\n보유", size=7.5, color=P["dim"])


diagram("22-driver-structs", draw, w=13, h=5.8, xmax=100, ymax=43)

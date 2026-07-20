"""CH12 §1 로그가 스택에서 내 sink 까지 도달하는 경로."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 20, 22, 13, P["blue"])
    d.text(13, 29.5, "스택 내부", size=9.4)
    d.text(13, 24.5, "LOG_DEBUG / LOG_INFO\nLOG_WARNING / LOG_ERROR\nLOG_CRITICAL", size=8.3, color=P["dim"])

    d.arrow(24, 26.5, 30, 26.5, color=P["accent"])

    d.box(30, 20, 22, 13, P["green"])
    d.text(41, 29.5, "CAN_stack_log(level, text)", size=8.8)
    d.text(41, 24.5, "레벨 필터\ncurrentLogLevel 미만은\n여기서 버려진다", size=8.3, color=P["dim"])

    d.arrow(52, 26.5, 57, 26.5, color=P["accent"])

    d.box(57, 20, 22, 13, P["purple"])
    d.text(68, 29.5, "등록된 sink 포인터", size=9)
    d.text(68, 24.5, "set_can_stack_logger_sink()\n로 넘긴 객체", size=8.3, color=P["dim"])

    d.arrow(79, 26.5, 83, 26.5, color=P["accent"])

    d.box(83, 20, 15, 13, P["chip"])
    d.text(90.5, 26.5, "내 클래스의\nsink_CAN_stack_log()", size=8.4, color=P["dim"])

    # 출력 대상
    for i, (x, label) in enumerate([(30, "stdout"), (48, "파일"), (66, "spdlog 등"), (84, "원격 수집")]):
        d.box(x, 4, 14, 8, P["gray"])
        d.text(x + 7, 8, label, size=8.8, color=P["dim"])
        d.arrow(90.5, 20, x + 7, 12, color=P["violet"], lw=1.2)

    d.text(13, 8, "레퍼런스만 저장하므로\nsink 객체는 static 이어야 한다", size=8.6, color=P["dim"])


diagram("12-logger-pipeline", draw, w=13, h=4.6, ymax=36)

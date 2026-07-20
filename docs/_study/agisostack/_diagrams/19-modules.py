"""CH19 라이브러리 모듈 구성 — 3개 CMake 타겟과 헤더 그룹 (light/dark PNG)."""
from _common import diagram

TOP = 37.0  # 컬럼 상단


def draw(d):
    P = d.P

    cols = [
        (2, 28, P["gray"], "isobus::Utility", "utility/", [
            "system_timing.hpp",
            "event_dispatcher.hpp",
            "iop_file_interface.hpp",
            "thread_synchronization.hpp",
            "data_span.hpp",
        ]),
        (33, 36, P["blue"], "isobus::Isobus", "isobus/", [
            "can_network_manager.hpp",
            "can_control_function.hpp",
            "can_NAME.hpp / can_NAME_filter.hpp",
            "can_transport_protocol*.hpp",
            "isobus_virtual_terminal_client.hpp",
            "isobus_task_controller_client.hpp",
            "isobus_*_interface.hpp",
        ]),
        (71, 27, P["brown"], "isobus::HardwareIntegration", "hardware_integration/", [
            "can_hardware_interface.hpp",
            "can_hardware_plugin.hpp",
            "socket_can_interface.hpp",
            "twai_plugin.hpp / mcp2515_*.hpp",
            "available_can_drivers.hpp",
        ]),
    ]

    for x, w, fc, target, folder, items in cols:
        h = 9.0 + len(items) * 3.9
        d.box(x, TOP - h, w, h, fc)
        d.text(x + w / 2, TOP - 3.0, target, size=11, weight="bold")
        d.text(x + w / 2, TOP - 6.2, folder, size=8.5, color=P["dim"], style="italic")
        for i, it in enumerate(items):
            y = TOP - 10.5 - i * 3.9
            d.box(x + 1.6, y - 1.5, w - 3.2, 3.0, P["chip"], lw=0.9)
            d.text(x + w / 2, y, it, size=8.2, color=P["text"])

    # 의존 방향
    d.arrow(33, 19, 30, 19, color=P["accent"], lw=1.6)
    d.arrow(71, 19, 69, 19, color=P["accent"], lw=1.6)
    d.text(31.5, 21, "의존", size=8, color=P["dim"])
    d.text(70, 21, "의존", size=8, color=P["dim"])

    # 애플리케이션
    d.box(28, 39, 45, 5.5, P["green"])
    d.text(50.5, 41.7, "애플리케이션 (사용자 코드)", size=10.5, weight="bold")
    d.arrow(50.5, 39, 50.5, TOP, color=P["accent"], lw=1.6)
    d.arrow(38, 39, 16, TOP + 0.2, color=P["edge"], lw=1.2, ls="--", rad=0.1)
    d.arrow(64, 39, 84, TOP + 0.2, color=P["edge"], lw=1.2, ls="--", rad=-0.1)


diagram("19-modules", draw, w=12.5, h=6.0, ymax=46)

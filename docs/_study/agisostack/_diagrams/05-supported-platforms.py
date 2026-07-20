"""CH5 §1 공식 지원 플랫폼과 기본 CAN 드라이버 매핑."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(3, 30, 94, 14, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 41.4, "공식 지원 플랫폼 (소스 빌드)", size=11, weight="bold",
           color=P["accent"])

    names = ["Ubuntu Linux\n(WSL 제외)", "Raspberry Pi OS\n(Raspbian)", "RHEL",
             "Windows", "MacOS", "ESP32"]
    fills = [P["blue"], P["blue"], P["blue"], P["green"], P["purple"], P["brown"]]
    for i, (n, fc) in enumerate(zip(names, fills)):
        x = 5.5 + i * 15.2
        d.box(x, 32, 13.5, 6.6, fc)
        d.text(x + 6.75, 35.3, n, size=8.5)

    # 기본 CAN 드라이버 행
    d.text(50, 26.5, "CMake 기본 선택 CAN 드라이버", size=10, color=P["dim"])
    drivers = ["SocketCAN", "SocketCAN", "SocketCAN",
               "WindowsPCANBasic", "MacCANPCAN", "TWAI (권장)"]
    for i, drv in enumerate(drivers):
        x = 5.5 + i * 15.2
        d.arrow(x + 6.75, 32, x + 6.75, 23.5, color=P["orange"], lw=1.4)
        d.box(x, 16.5, 13.5, 6.2, P["chip"])
        d.text(x + 6.75, 19.6, drv, size=8.5)

    # 비지원 안내
    d.box(3, 4, 94, 8.5, P["chip"], ec=P["dim"])
    d.text(50, 9.6, "WSL 미지원 — WSL 커널이 기본적으로 SocketCAN을 지원하지 않음",
           size=9.5, color=P["dim"])
    d.text(50, 6.4, "그 외 플랫폼도 동작할 수 있으나 공식 지원 대상은 아님",
           size=9.5, color=P["dim"])


diagram("05-supported-platforms", draw, w=12.5, h=5.6, ymax=46)

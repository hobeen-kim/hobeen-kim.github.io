"""CH18 §1 PlatformIO 프로젝트 셋업 순서 — 설치부터 빌드·플래시까지."""
from _common import diagram


def draw(d):
    P = d.P

    steps = [
        ("설치", "VS Code · Git\nPlatformIO 확장", P["gray"]),
        ("새 프로젝트", "보드 선택\nframework = espidf", P["blue"]),
        ("C++ 전환", "main.c → main.cpp\nextern \"C\" app_main", P["blue"]),
        ("라이브러리 추가", "lib_deps =\nAgIsoStack-plus-plus.git", P["purple"]),
        ("menuconfig", "PThreads 스택 8192\nconfigTICK_RATE_HZ 250", P["brown"]),
        ("빌드 · 플래시", "esptool 업로드\n시리얼 모니터 115200", P["green"]),
    ]

    x = 2
    for i, (title, body, fc) in enumerate(steps):
        d.box(x, 24, 14.5, 14, fc)
        d.text(x + 7.25, 34.5, title, size=10.5, weight="bold")
        d.text(x + 7.25, 29, body, size=8.6, color=P["dim"])
        if i < len(steps) - 1:
            d.arrow(x + 16.5, 31, x + 18.5, 31, color=P["accent"])
        x += 16.3

    # 아래: 코드에서 해야 할 일
    d.box(18, 5, 64, 12, P["chip"])
    d.text(50, 14, "main.cpp 안에서", size=10, weight="bold")
    d.text(50, 9.5,
           "TWAI 설정 (GPIO 21/22 · 250 kbit/s · 필터 없음)  →  TWAIPlugin 생성\n"
           "→ CANHardwareInterface 채널 할당 · start()  →  NAME 설정 · 내부 CF 생성",
           size=9, color=P["dim"])
    d.arrow(50, 24, 50, 17, color=P["edge"], style="-|>", lw=1.3)


diagram("18-platformio-flow", draw, w=13, h=5.2, ymax=41)

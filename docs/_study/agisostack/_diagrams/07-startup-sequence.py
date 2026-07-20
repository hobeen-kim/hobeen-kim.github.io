"""CH7 요약 — Hello World 프로그램의 기동·종료 순서."""
from _common import diagram


def draw(d):
    P = d.P

    steps = [
        ("1. 하드웨어 계층", "SocketCANInterface(\"can0\")\nset_number_of_can_channels(1)\nassign_can_channel_frame_handler(0, ...)", P["brown"]),
        ("2. 스레드 기동", "CANHardwareInterface::start()\n+ get_is_valid() 확인", P["brown"]),
        ("3. 시그널 핸들러", "std::signal(SIGINT, ...)\nrunning = false", P["gray"]),
        ("4. NAME 구성", "set_function_code(...)\nset_manufacturer_code(1407) 등", P["blue"]),
        ("5. ICF 생성", "create_internal_control_function\n(myNAME, 0, 0x1C)", P["blue"]),
        ("6. 주소 클레임 대기", "sleep_for(1000ms)", P["purple"]),
        ("7. 메시지 송신", "send_can_message(0xEF00, ...)", P["green"]),
        ("8. 정리", "CANHardwareInterface::stop()", P["gray"]),
    ]

    x = 2.0
    w = 22.5
    gap = 2.0
    ys = [26, 4]
    for i, (title, body, fc) in enumerate(steps):
        row = i // 4
        col = i % 4
        cx = x + col * (w + gap)
        cy = ys[row]
        d.box(cx, cy, w, 16, fc)
        d.text(cx + w / 2, cy + 12.6, title, size=10.5, weight="bold")
        d.text(cx + w / 2, cy + 6.5, body, size=8.8, color=P["dim"])
        if col < 3:
            d.arrow(cx + w, cy + 8, cx + w + gap, cy + 8)

    # 줄바꿈 화살표 (4 → 5): 두 행 사이 빈 통로로 우회
    right = x + 3 * (w + gap) + w / 2
    left = x + w / 2
    mid = ys[1] + 16 + (ys[0] - (ys[1] + 16)) / 2
    d.arrow(right, ys[0], right, mid, color=P["accent"], style="-")
    d.arrow(right, mid, left, mid, color=P["accent"], style="-")
    d.arrow(left, mid, left, ys[1] + 16, color=P["accent"])


diagram("07-startup-sequence", draw, w=13, h=5.2, ymax=46)

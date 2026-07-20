"""README 학습 로드맵 — 6개 섹션 순차 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("시작하기 (CH1~4)", "개요 · ISOBUS 개념 · Control Function/NAME · 전송 계층", P["blue"]),
        ("설치와 빌드 (CH5~6)", "CMake 통합 · 플랫폼별 설치 · 개발자 가이드", P["gray"]),
        ("기본 통신 (CH7~12)", "Hello World · 수신 · 목적지 · 전송 계층 · PGN 요청 · 로깅", P["green"]),
        ("애플리케이션 계층 (CH13~16)", "Virtual Terminal · DDOP · Task Controller · 작업기 메시지", P["purple"]),
        ("하드웨어와 이식 (CH17~18)", "HardwareInterface · ESP32/PlatformIO", P["brown"]),
        ("레퍼런스 (CH19 · 부록)", "API 구조 · FAQ/릴리스/라이선스 · 참고 자료", P["chip"]),
    ]

    top = 60.0
    bh = 8.0
    gap = 2.4
    for i, (title, body, fc) in enumerate(stages):
        y = top - i * (bh + gap) - bh
        d.box(14, y, 72, bh, fc)
        d.text(18, y + bh - 2.9, title, size=11.5, weight="bold", ha="left")
        d.text(18, y + 2.6, body, size=9, color=P["dim"], ha="left")
        if i < len(stages) - 1:
            d.arrow(50, y, 50, y - gap, color=P["accent"], lw=1.6)


diagram("00-roadmap", draw, w=9.5, h=7.4, ymax=62)

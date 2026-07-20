"""CH6 §2~5 개발자 워크플로 — clone → configure → build → test/examples/docs."""
from _common import diagram


def draw(d):
    P = d.P

    # 구성 단계에서 주는 CMake 옵션
    d.box(38, 42, 34, 10, P["brown"])
    d.text(55, 49.4, "구성 단계 CMake 옵션", size=9.5, weight="bold")
    d.text(55, 45.4, "-DCAN_DRIVER=…  /  -DBUILD_TESTING=ON  /  -DBUILD_EXAMPLES=ON",
           size=8)
    d.arrow(55, 42, 55, 38, color=P["accent"], lw=1.5)

    # 파이프라인
    d.box(2, 26, 17, 12, P["chip"])
    d.text(10.5, 35.2, "사전 준비물", size=9.5, weight="bold", color=P["dim"])
    d.text(10.5, 30.5, "Git / CMake\nC++ 컴파일러", size=9)

    steps = [
        (24, P["blue"], "clone", "git clone …\nAgIsoStack-plus-plus"),
        (46, P["green"], "configure", "cmake -S . -B build"),
        (68, P["purple"], "build", "cmake --build build"),
    ]
    for x, fc, title, body in steps:
        d.box(x, 26, 17, 12, fc)
        d.text(x + 8.5, 35.2, title, size=9.5, weight="bold")
        d.text(x + 8.5, 30.5, body, size=9)

    d.arrow(19, 32, 24, 32)
    d.arrow(41, 32, 46, 32)
    d.arrow(63, 32, 68, 32)

    # 산출물
    outs = [
        (4, "Doxygen 문서", "doxygen doxyfile\n→ docs/html/index.html"),
        (28, "예제", "./examples/<example_name>"),
        (52, "테스트", "cd build\nctest"),
        (76, "정적 라이브러리", "isobus / HardwareIntegration\n/ Utility"),
    ]
    for x, title, body in outs:
        d.box(x, 4, 20, 12, P["gray"])
        d.text(x + 10, 13.4, title, size=9.5, weight="bold")
        d.text(x + 10, 8.6, body, size=8.5)

    d.arrow(76.5, 26, 38, 16, color=P["orange"], rad=0.12)
    d.arrow(76.5, 26, 62, 16, color=P["orange"], rad=0.06)
    d.arrow(80, 26, 86, 16, color=P["orange"])

    d.arrow(28, 26, 16, 16, color=P["violet"], rad=0.12, ls="--")
    d.text(2, 21, "빌드와 무관 —\n소스 트리에서 직접", size=8,
           color=P["violet"], ha="left")


diagram("06-build-flow", draw, w=13, h=6.4, ymax=54)

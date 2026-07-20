"""CH5 §3 프로젝트 통합 방식 3가지 — Git Submodule / FetchContent / Precompiled."""
from _common import diagram


def draw(d):
    P = d.P

    # 좌측: 내 프로젝트
    d.box(2, 16, 18, 28, P["gray"], ec=P["accent"], lw=1.8)
    d.text(11, 41.4, "내 프로젝트", size=11, weight="bold", color=P["accent"])
    d.box(4.5, 31, 13, 6.5, P["chip"])
    d.text(11, 34.2, "CMakeLists.txt", size=9.5)
    d.box(4.5, 19, 13, 7.5, P["chip"])
    d.text(11, 22.7, "my_app\n(executable)", size=9.5)

    # 방식 1
    d.box(28, 38, 34, 12, P["blue"])
    d.text(45, 47.4, "Git Submodule", size=10.5, weight="bold")
    d.text(45, 42.8, "git submodule add …\n소스가 프로젝트 트리 안에 놓인다", size=9)

    # 방식 2
    d.box(28, 24, 34, 12, P["green"])
    d.text(45, 33.4, "CMake FetchContent", size=10.5, weight="bold")
    d.text(45, 28.8, "FetchContent_Declare / MakeAvailable\n구성 시점에 GitHub에서 받아온다", size=9)

    # 방식 3
    d.box(28, 10, 34, 12, P["chip"], ec=P["dim"])
    d.text(45, 19.4, "Precompiled (미제공)", size=10.5, weight="bold", color=P["dim"])
    d.text(45, 14.8, "공식 바이너리 배포 없음\n→ 소스 빌드만 지원", size=9, color=P["dim"])

    # 우측: 링크 타겟
    d.box(70, 24, 28, 22, P["purple"])
    d.text(84, 43.2, "isobus:: ALIAS 타겟", size=10.5, weight="bold")
    d.text(84, 34.5, "isobus::Isobus\nisobus::HardwareIntegration\nisobus::Utility\nThreads::Threads", size=9.5)

    # 프로젝트 → 방식
    d.arrow(20, 34, 28, 44, rad=0.12)
    d.arrow(20, 31, 28, 30)
    d.arrow(20, 28, 28, 16, rad=-0.12, ls=":", color=P["dim"])

    # 방식 → 타겟
    d.arrow(62, 44, 70, 38, rad=-0.1)
    d.arrow(62, 30, 70, 32, rad=0.1)
    d.text(66, 22, "add_subdirectory /\nMakeAvailable", size=8, color=P["dim"])

    # 타겟 → 실행 파일 링크
    d.arrow(84, 24, 84, 5, color=P["orange"], lw=1.6, style="-")
    d.arrow(84, 5, 11, 5, color=P["orange"], lw=1.6, style="-")
    d.arrow(11, 5, 11, 16, color=P["orange"], lw=1.6)
    d.text(45, 6.6, "target_link_libraries(my_app PRIVATE …)", size=8.5,
           color=P["orange"])


diagram("05-integration-methods", draw, w=12.5, h=6.4, ymax=52)

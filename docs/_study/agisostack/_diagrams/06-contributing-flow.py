"""CH6 §7 기여 절차 — 로컬 검증에서 머지까지의 게이트."""
from _common import diagram


def draw(d):
    P = d.P

    # 로컬 단계
    d.box(2, 24, 30, 20, P["blue"])
    d.text(17, 41.2, "로컬 작업", size=10.5, weight="bold")
    d.text(17, 34.5, "clang-format -i\ncmake-format -i\npre-commit-hook.sh 연결", size=9)
    d.text(17, 27.5, "코딩 규칙: snake_case 함수\ncamelCase 변수 / C++14 한정", size=8.5,
           color=P["dim"])

    # PR
    d.box(38, 30, 24, 14, P["green"])
    d.text(50, 41.2, "Pull Request", size=10.5, weight="bold")
    d.text(50, 35.5, "MIT 이하 라이선스 코드만\n신규 코드 커버리지 80% 목표", size=9)

    # 자동 체크
    d.box(38, 6, 24, 18, P["purple"])
    d.text(50, 21.2, "자동 사전 머지 체크", size=10.5, weight="bold")
    d.text(50, 14, "컴파일 GitHub Action\nclang-format / cmake-format\nDoxygen 무경고", size=9)

    # 리뷰
    d.box(68, 30, 30, 14, P["brown"])
    d.text(83, 41.2, "메인테이너 코드 리뷰", size=10.5, weight="bold")
    d.text(83, 35.5, "스타일 규칙 수동 확인\n행동 강령 준수 필요", size=9)

    # 머지
    d.box(68, 8, 30, 14, P["gray"], ec=P["accent"], lw=1.8)
    d.text(83, 19.2, "Merge", size=10.5, weight="bold", color=P["accent"])
    d.text(83, 13.5, "자동 체크 전부 통과 +\n리뷰 승인", size=9)

    d.arrow(32, 37, 38, 37)
    d.arrow(50, 30, 50, 24, color=P["orange"])
    d.arrow(62, 37, 68, 37)
    d.arrow(83, 30, 83, 22)
    d.arrow(62, 15, 68, 15, color=P["orange"])
    d.arrow(44, 22, 32, 27, color=P["violet"], rad=0.25, ls="--")
    d.text(37, 18.5, "실패 시 수정", size=8, color=P["violet"])


diagram("06-contributing-flow", draw, w=12.5, h=5.8, ymax=46)

"""CH14 빌드 파이프라인 — Soong/Kati가 만든 ninja를 Ninja가 실행해 out/ 산출 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 입력 (좌측 상/하)
    d.box(2, 33, 20, 9, P["blue"])
    d.text(12, 37.5, "Android.bp\n(Blueprint)", size=10)
    d.box(2, 9, 20, 9, P["brown"])
    d.text(12, 13.5, "Android.mk\n(GNU Make)", size=10)

    # 변환기
    d.box(28, 33, 19, 9, P["green"])
    d.text(37.5, 37.5, "Soong\n(soong_build)", size=10)
    d.box(28, 9, 19, 9, P["purple"])
    d.text(37.5, 13.5, "Kati\n(ckati)", size=10)

    # 통합 ninja
    d.box(53, 20.5, 18, 10, P["gray"], ec=P["accent"], lw=1.8)
    d.text(62, 25.5, "build.ninja\n(통합 빌드 그래프)", size=10)

    # Ninja 실행
    d.box(78, 20.5, 19, 10, P["blue"])
    d.text(87.5, 25.5, "Ninja\n(증분 실행)", size=10)

    # 산출물
    d.box(78, 4, 19, 9, P["chip"])
    d.text(87.5, 8.5, "out/target/product/\n<device>/*.img", size=9)

    # 화살표
    d.arrow(22, 37.5, 28, 37.5)
    d.arrow(22, 13.5, 28, 13.5)
    d.arrow(47, 37.5, 62, 30.5, color=P["orange"])
    d.text(53, 35, ".ninja 생성", size=8, color=P["orange"])
    d.arrow(47, 13.5, 62, 20.5, color=P["violet"])
    d.text(53, 15.5, ".ninja 생성", size=8, color=P["violet"])
    d.arrow(71, 25.5, 78, 25.5, color=P["accent"])
    d.arrow(87.5, 20.5, 87.5, 13, color=P["accent"])
    d.text(90.5, 16.7, "이미지", size=8, color=P["dim"])


diagram("14-build-pipeline", draw, w=13, h=5, xmax=100, ymax=46)

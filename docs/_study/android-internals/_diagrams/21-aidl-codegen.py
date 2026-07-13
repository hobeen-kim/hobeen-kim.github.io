"""CH21 AIDL 코드 생성 — 하나의 .aidl에서 백엔드별 생성물 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 입력 .aidl
    d.box(3, 18, 22, 12, P["purple"], ec=P["accent"], lw=1.7)
    d.text(14, 26, "ICanAccessService.aidl", size=11, weight="bold")
    d.text(14, 22.5, "인터페이스 정의\n(메서드 · parcelable)", size=8.3, color=P["dim"])

    # aidl 컴파일러
    d.box(31, 20, 16, 8, P["gray"], ec=P["accent"], lw=1.5)
    d.text(39, 24, "aidl 컴파일러", size=9.5, weight="bold", color=P["accent"])

    d.arrow(25, 24, 31, 24, color=P["orange"])

    # 백엔드별 생성물
    backends = [
        ("java", "Stub / Proxy\nandroid.os.IInterface", P["blue"], 32),
        ("cpp", "BnCanAccessService /\nBpCanAccessService\nlibbinder (sp<>)", P["green"], 23),
        ("ndk", "aidl::...::BnCanAccessService\nlibbinder_ndk (AIBinder*)", P["brown"], 14),
        ("rust", "trait ICanAccessService\nbinder crate", P["purple"], 5),
    ]
    for tag, gen, fc, y in backends:
        d.box(56, y, 40, 7.5, fc)
        d.text(60, y + 3.75, tag, size=9, weight="bold", color=P["accent"])
        d.text(78, y + 3.75, gen, size=8, color=P["dim"])
        d.arrow(47, 24, 56, y + 3.75, color=P["dim"], rad=0.05)

    d.text(14, 10, "한 정의 →\n언어별 프록시/스텁\n자동 생성", size=8.5, color=P["dim"])
    d.text(39, 15.5, "vendor 데몬은 ndk 백엔드 사용", size=8, color=P["orange"])


diagram("21-aidl-codegen", draw, w=12.5, h=5.6, xmax=100, ymax=42)

"""CH20 dex2oat 산출물 — DEX에서 VDEX/OAT/ART 파일 관계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 입력: APK 안의 DEX
    d.box(4, 20, 20, 12, P["blue"])
    d.text(14, 28.5, "app.apk", size=9.5, weight="bold")
    d.text(14, 24.5, "classes.dex", size=8.3, color=P["dim"])

    # dex2oat
    d.box(32, 19, 20, 14, P["gray"], ec=P["accent"], lw=1.7)
    d.text(42, 29.5, "dex2oat", size=10.5, weight="bold", color=P["accent"])
    d.text(42, 25, "compiler filter\n에 따라 컴파일", size=8, color=P["dim"])

    d.arrow(24, 26, 32, 26, color=P["orange"])

    # 산출물 3종 → /data/dalvik-cache 또는 oat/
    outs = [
        ("app.vdex", "검증된 DEX + quicken 정보\n(재검증 생략용)", P["green"], 36),
        ("app.odex (OAT)", "AOT 네이티브 코드\nELF 컨테이너", P["brown"], 22),
        ("app.art", "힙 이미지 (미리 초기화된\n객체·클래스)", P["purple"], 8),
    ]
    for name, desc, fc, y in outs:
        d.box(64, y, 32, 11, fc)
        d.text(80, y + 8, name, size=9.3, weight="bold")
        d.text(80, y + 3.5, desc, size=7.6, color=P["dim"])
        d.arrow(52, 26, 64, y + 5.5, color=P["edge"], lw=1.2, rad=0.08)

    d.text(80, 3.5, "저장 위치: /data/app/.../oat/<abi>/ · boot는 /data/dalvik-cache",
           size=7.4, color=P["dim"], ha="right")


diagram("20-dex2oat-files", draw, w=13, h=5.6, ymax=50)

"""CH17 APK 해부 — ZIP 엔트리 구성과 APK Signing Block 위치 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 좌: APK ZIP 내부 엔트리
    d.box(3, 5, 40, 40, P["gray"], ec=P["accent"], lw=1.6)
    d.text(23, 42, "app.apk (ZIP 컨테이너)", size=10.5, weight="bold",
           color=P["accent"])
    entries = [
        ("AndroidManifest.xml", "바이너리 XML (aapt2 dump)", P["blue"]),
        ("classes.dex[, classes2.dex]", "DEX 바이트코드", P["green"]),
        ("resources.arsc", "컴파일된 리소스 테이블", P["brown"]),
        ("res/  ·  assets/", "리소스 · 원본 에셋", P["purple"]),
        ("lib/<abi>/*.so", "네이티브 라이브러리", P["blue"]),
        ("META-INF/", "v1(JAR) 서명 · 매니페스트", P["chip"]),
    ]
    for i, (name, desc, fc) in enumerate(entries):
        y = 37 - i * 5.4
        d.box(6, y, 34, 4.4, fc)
        d.text(23, y + 2.9, name, size=8.3, weight="bold")
        d.text(23, y + 1.0, desc, size=7.2, color=P["dim"])

    # 우: 파일 물리 레이아웃 (서명 블록 위치)
    d.box(52, 5, 44, 40, P["chip"])
    d.text(74, 42, "파일 물리 레이아웃", size=10, weight="bold", color=P["dim"])
    layout = [
        ("ZIP 엔트리 (콘텐츠)", "압축된 파일 데이터", P["blue"]),
        ("APK Signing Block", "v2/v3/v4 서명 (ZIP 밖)", P["green"]),
        ("Central Directory", "엔트리 인덱스", P["brown"]),
        ("End of Central Dir", "EOCD 레코드", P["purple"]),
    ]
    for i, (name, desc, fc) in enumerate(layout):
        y = 35 - i * 8
        d.box(55, y, 38, 6.5, fc)
        d.text(74, y + 4.4, name, size=9, weight="bold")
        d.text(74, y + 1.7, desc, size=7.6, color=P["dim"])
        if i < 3:
            d.arrow(74, y, 74, y - 1.5, color=P["orange"])

    d.arrow(43, 25, 52, 30, color=P["edge"], lw=1.3, rad=0.1)
    d.text(47.5, 29.5, "zipalign", size=7.3, color=P["dim"])


diagram("17-apk-structure", draw, w=12.5, h=5.8, ymax=48)

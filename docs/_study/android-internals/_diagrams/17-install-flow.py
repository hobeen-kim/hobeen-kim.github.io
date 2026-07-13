"""CH17 설치 파이프라인 — pm install 이면의 session→검증→installd→PMS 등록."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("pm install / PackageInstaller", "install session 생성, APK 스트리밍", P["blue"]),
        ("검증", "서명·무결성·minSdk 확인\nPackageManagerService", P["green"]),
        ("installd", "/data/app/<pkg>-<rand> 생성\ndexopt(dex2oat) 트리거", P["brown"]),
        ("PMS 등록", "packages.xml · packages.list\n권한 부여 · uid 배정", P["purple"]),
        ("BOOT_COMPLETED 이후 사용 가능", "PACKAGE_ADDED 브로드캐스트", P["chip"]),
    ]
    for i, (name, desc, fc) in enumerate(stages):
        y = 40 - i * 8
        d.box(18, y, 64, 6.5, fc)
        d.text(50, y + 4.5, name, size=10, weight="bold",
               color=P["accent"] if i < 4 else P["dim"])
        d.text(50, y + 1.7, desc, size=8, color=P["dim"])
        if i < 4:
            d.arrow(50, y, 50, y - 1.5, color=P["orange"])

    # 좌측 주석
    d.text(14, 43.2, "요청", size=8, color=P["dim"], ha="right")
    d.text(86, 3.5, "installd는 root, dexopt는 별도 프로세스로 격리",
           size=7.6, color=P["dim"], ha="right")


diagram("17-install-flow", draw, w=11, h=6.4, ymax=48)

"""CH4 파일시스템 트리 — system-as-root 아래 주요 최상위 디렉토리와 역할."""
from _common import diagram


def draw(d):
    P = d.P

    # 루트
    d.box(4, 22, 14, 6, P["accent"])
    d.text(11, 25, "/  (system-\nas-root)", size=9, weight="bold",
           color=P["bg"])

    branches = [
        ("/system", "bin·lib64·framework·priv-app", P["blue"], 45),
        ("/vendor", "HAL·firmware·VNDK 경계", P["brown"], 37),
        ("/product", "OEM 앱·리소스", P["purple"], 29),
        ("/system_ext", "system 확장(파티션 분리)", P["blue"], 21),
        ("/data", "앱 데이터·CE/DE 스토리지", P["green"], 13),
        ("/vendor(+odm)", "벤더/ODM 커스텀", P["brown"], 5),
    ]
    for name, desc, fc, y in branches:
        d.box(30, y, 20, 6, fc)
        d.text(40, y + 3, name, size=9, weight="bold")
        d.box(54, y, 42, 6, P["chip"])
        d.text(56, y + 3, desc, size=8.5, ha="left", color=P["dim"])
        d.arrow(18, 25, 30, y + 3, color=P["edge"], lw=1.1, rad=0.05)

    # /data 하위 강조
    d.text(75, 44.5, "심볼릭 링크: /bin→/system/bin, /etc→/system/etc",
           size=8, color=P["dim"], ha="center", style="italic")


diagram("04-fs-tree", draw, w=12, h=6, ymax=52)

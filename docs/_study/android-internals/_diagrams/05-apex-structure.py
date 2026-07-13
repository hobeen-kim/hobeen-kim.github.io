"""CH5 APEX 구조와 activate — 파일 구성과 apexd verify→mount→activate 흐름."""
from _common import diagram


def draw(d):
    P = d.P

    # 좌: APEX 파일 구조
    d.box(4, 6, 34, 36, P["gray"], ec=P["accent"], lw=1.6)
    d.text(21, 39.5, "com.android.*.apex (ZIP)", size=10, weight="bold",
           color=P["accent"])
    inner = [
        ("apex_payload.img", "ext4/erofs 이미지 (실제 파일)", P["blue"]),
        ("apex_manifest.pb", "이름·버전 메타데이터", P["green"]),
        ("apex_pubkey", "서명 검증 공개키", P["purple"]),
        ("AndroidManifest.xml", "패키지 관리자용 메타", P["brown"]),
    ]
    for i, (name, desc, fc) in enumerate(inner):
        y = 32 - i * 7
        d.box(7, y, 28, 5.5, fc)
        d.text(21, y + 3.7, name, size=8.5, weight="bold")
        d.text(21, y + 1.4, desc, size=7.5, color=P["dim"])

    # 우: apexd 활성화 파이프라인
    steps = [
        ("verify", "AVB 서명·해시 검증", P["blue"]),
        ("mount", "payload.img를 loop\n마운트 → /apex/<name>@ver", P["brown"]),
        ("activate", "/apex/<name> 바인드\nlinkerconfig 갱신", P["green"]),
    ]
    for i, (name, desc, fc) in enumerate(steps):
        y = 32 - i * 11
        d.box(52, y, 40, 8.5, fc)
        d.text(72, y + 6, f"apexd: {name}", size=9.5, weight="bold",
               color=P["accent"])
        d.text(72, y + 2.6, desc, size=8, color=P["dim"])
        if i < 2:
            d.arrow(72, y, 72, y - 2.5, color=P["orange"])

    d.arrow(38, 24, 52, 28, color=P["edge"], lw=1.3, rad=0.1)


diagram("05-apex-structure", draw, w=12, h=5.6, ymax=44)

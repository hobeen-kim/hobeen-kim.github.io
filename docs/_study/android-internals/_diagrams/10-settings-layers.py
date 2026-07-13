"""CH10 설정의 계층 — 여러 설정 소스가 실효값으로 수렴하는 구조 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 설정 소스들 (왼쪽 세로 스택) — 위가 빌드타임, 아래가 런타임/원격
    sources = [
        ("config.xml (framework-res)", "빌드타임 기본값", P["gray"]),
        ("RRO 오버레이 (/vendor, /product)", "리소스 런타임 치환", P["brown"]),
        ("CarrierConfig", "통신사·SIM별 값", P["purple"]),
        ("settings (system/secure/global)", "런타임 사용자 설정", P["blue"]),
        ("device_config / aconfig", "원격 플래그·기능 토글", P["green"]),
    ]
    x, w, h, gap = 4, 40, 7, 1.6
    top = 44
    ys = [top - i * (h + gap) for i in range(len(sources))]
    for (title, sub, fc), y in zip(sources, ys):
        d.box(x, y, w, h, fc)
        d.text(x + w / 2, y + h * 0.62, title, size=9.5, weight="bold")
        d.text(x + w / 2, y + h * 0.24, sub, size=8, color=P["dim"])

    # 실효 설정값 (오른쪽)
    d.box(62, 16, 32, 22, P["gray"], ec=P["accent"], lw=1.8)
    d.text(78, 34.5, "실효 설정값", size=11, weight="bold", color=P["accent"])
    d.text(78, 26, "앱·프레임워크가\n실제로 읽는 값\n(뒤 소스가 앞을 오버라이드)",
           size=9, color=P["dim"])

    for y in ys:
        d.arrow(x + w, y + h / 2, 62, 27, color=P["accent"], lw=1.3, rad=0.03)

    # sysconfig 는 권한 allowlist — 별도 경로
    d.box(4, 1.5, 40, 6, P["chip"])
    d.text(24, 4.5, "sysconfig (/etc/sysconfig, privapp-permissions)",
           size=8.5, color=P["dim"])
    d.arrow(44, 4.5, 78, 16, color=P["orange"], lw=1.3, rad=-0.15)
    d.text(60, 6, "권한 부여", size=8, color=P["orange"])


diagram("10-settings-layers", draw, w=12, h=6.6, ymax=52)

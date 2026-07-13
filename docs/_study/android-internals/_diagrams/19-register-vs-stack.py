"""CH19 레지스터 기반 vs 스택 기반 VM — a = b + c 실행 대비."""
from _common import diagram


def draw(d):
    P = d.P

    # 좌: 스택 기반 (JVM)
    d.box(4, 6, 42, 36, P["gray"], ec=P["accent"], lw=1.5)
    d.text(25, 39, "스택 기반 (JVM 바이트코드)", size=9.8, weight="bold",
           color=P["accent"])
    jvm = ["iload b", "iload c", "iadd", "istore a"]
    for i, op in enumerate(jvm):
        d.box(8, 32 - i * 5, 20, 4, P["blue"])
        d.text(18, 34 - i * 5, op, size=8.5)
    d.text(37, 30, "피연산자를\n스택에 push/pop", size=8, color=P["dim"])
    d.text(25, 9, "4개 명령 · 명령이 짧음", size=7.8, color=P["dim"])

    # 우: 레지스터 기반 (Dalvik/DEX)
    d.box(54, 6, 42, 36, P["gray"], ec=P["accent"], lw=1.5)
    d.text(75, 39, "레지스터 기반 (DEX 바이트코드)", size=9.8, weight="bold",
           color=P["accent"])
    dex = ["add-int v0, v1, v2"]
    d.box(58, 27, 34, 5, P["green"])
    d.text(75, 29.5, dex[0], size=9, weight="bold")
    d.text(75, 22, "가상 레지스터 v0..vN에서\n직접 연산", size=8, color=P["dim"])
    d.text(75, 9, "1개 명령 · 명령당 정보량 많음", size=7.8, color=P["dim"])

    d.arrow(46, 24, 54, 24, color=P["orange"], lw=1.6)
    d.text(50, 25.6, "명령 수↓\n인출 오버헤드↓", size=6.8, color=P["orange"])


diagram("19-register-vs-stack", draw, w=13, h=5.6, ymax=46)

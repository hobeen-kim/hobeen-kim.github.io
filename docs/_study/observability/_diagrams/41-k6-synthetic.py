"""CH41 k6·Synthetic Monitoring — 능동 관측 구조 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "k6 · Synthetic Monitoring — 능동적(active) 관측", size=20, weight="bold")
text(50, 56.6, "합성 트래픽을 직접 만들어 확인한다  —  수동적(passive) 관측(메트릭·로그·RUM)의 반대편",
     size=12, color=C_DIM)

# ================= left column: two sources =================
box(2, 33, 30, 19, C_GREEN)
text(17, 49.6, "k6 — 부하 테스트", size=13, weight="bold")
text(17, 47.4, "JS 시나리오 · 배포 전/정기 실행", size=9, color=C_DIM)
for i, (t, d) in enumerate([
    ("VU · executor", "가상 사용자 램프업 · 시나리오 조합"),
    ("checks · thresholds", "p95<300ms 같은 SLO를 코드로 검증"),
    ("k6 browser", "실제 브라우저로 Web Vitals 측정"),
]):
    yy = 44.5 - i * 3.9
    box(4, yy - 1.6, 26, 3.2, "#1d2b24")
    text(17, yy + 0.5, t, size=9.5)
    text(17, yy - 0.9, d, size=7.8, color=C_DIM)

box(2, 10, 30, 19, C_BLUE)
text(17, 26.6, "Synthetic Monitoring — 상시 프로브", size=12.5, weight="bold")
text(17, 24.4, "글로벌 프로브 위치 + private probe", size=9, color=C_DIM)
for i, (t, d) in enumerate([
    ("HTTP · ping · DNS · TCP", "가용성 · 응답시간 · TLS 만료"),
    ("browser · scripted check", "k6 스크립트로 다단계 여정 검증"),
    ("traceroute", "네트워크 경로 진단"),
]):
    yy = 21.5 - i * 3.9
    box(4, yy - 1.6, 26, 3.2, "#1b232a")
    text(17, yy + 0.5, t, size=9.5)
    text(17, yy - 0.9, d, size=7.8, color=C_DIM)

# ================= center: target =================
box(40, 24, 20, 22, C_BROWN)
text(50, 43.6, "대상 시스템", size=13, weight="bold")
text(50, 41.0, "API · 웹 · DNS · 인증서", size=9.5, color=C_DIM)
text(50, 34.5, "사용자가 겪기 전에\n외부 관점에서\n먼저 두드려본다", size=10.5, color="#d4dae0")
text(50, 27.0, "내부 계측이 전혀 없어도\n측정 가능 (블랙박스 관점)", size=8.5,
     color=C_ACCENT, style="italic")

arrow(32, 42, 40, 40, color=C_ORANGE, lw=2.2)
text(36, 43.6, "부하 주입", size=8.5, color=C_ORANGE, weight="bold")
arrow(32, 19, 40, 28, color=C_ACCENT, lw=2.2)
text(35, 21.5, "정기 프로브", size=8.5, color=C_ACCENT, weight="bold")

# ================= right: results into LGTM =================
box(68, 24, 30, 28, C_GRAY)
text(83, 49.6, "결과 → LGTM 스택", size=13, weight="bold")
for i, (t, d) in enumerate([
    ("Prometheus / Mimir", "k6 remote write · probe_success 등 메트릭"),
    ("Loki", "check 실행 로그 · 실패 원인"),
    ("Grafana 대시보드", "지역별 가용성 · p95 추이 · 임계 비교"),
    ("Alerting · SLO", "uptime SLI → burn rate 알림 재사용"),
]):
    yy = 45 - i * 5.0
    box(70, yy - 2.0, 26, 4.0, "#1b232a")
    text(83, yy + 0.6, t, size=10)
    text(83, yy - 1.1, d, size=8, color=C_DIM)

arrow(60, 35, 68, 38, color=C_VIOLET, lw=2.2)
text(64, 38.2, "메트릭·로그", size=8.5, color=C_VIOLET, weight="bold")

# ================= bottom: blackbox_exporter comparison =================
box(40, 6, 58, 12, C_GRAY, ec=C_EDGE, lw=1.2)
text(69, 15.6, "blackbox_exporter와의 관계", size=11, weight="bold")
text(69, 11.2, "blackbox_exporter = 클러스터 내부에서 실행하는 셀프호스팅 프로브 (HTTP/TCP/ICMP/DNS, 8장)\n"
               "Synthetic Monitoring = 전 세계 프로브 위치에서 실행 + browser/scripted check까지 확장\n"
               "간단한 내부 가용성 체크는 blackbox로 충분 — 사용자 관점·다지역·다단계 여정이 필요할 때 SM으로",
     size=8.8, color="#d4dae0")

text(50, 2.6, "능동적 관측: 트래픽이 없어도 · 사용자가 겪기 전에 · 외부 관점에서 문제를 먼저 발견한다",
     size=10, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="k6 부하 주입"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="Synthetic 프로브"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="결과 메트릭·로그 적재"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "41-k6-synthetic.png")

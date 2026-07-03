"""CH36 게이트웨이 인증·인가와 컴포넌트 간 mTLS (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # ---- client ----
    d.box(3, 28, 18, 11, P["gray"])
    d.text(12, 35.5, "Prometheus /\nGrafana", size=10.5, weight="bold")
    d.text(12, 31.0, "(클라이언트)", size=8.5, color=P["dim"])

    # ---- gateway ----
    d.box(26, 26, 20, 15, P["brown"], ec=P["orange"], lw=1.8)
    d.text(36, 37.6, "Gateway", size=12, weight="bold", color=P["orange"])
    d.text(36, 33.4, "OAuth2 / JWT 검증", size=9, color=P["dim"])
    d.text(36, 30.4, "X-Scope-OrgID 주입", size=9, color=P["dim"])

    # ---- internal network group ----
    d.box(51, 8, 47, 40, P["chip"], ec=P["accent"], lw=1.4)
    d.text(74.5, 45.4, "내부 네트워크 (mTLS)", size=11, weight="bold", color=P["accent"])

    d.box(55, 34, 18, 6.5, P["blue"])
    d.text(64, 37.25, "Mimir\ndistributor", size=9.3)
    d.box(77, 34, 18, 6.5, P["purple"])
    d.text(86, 37.25, "Mimir\nquery-frontend", size=9)
    d.box(55, 15, 18, 6.5, P["blue"])
    d.text(64, 18.25, "ingester", size=10)
    d.box(77, 15, 18, 6.5, P["purple"])
    d.text(86, 18.25, "store-gateway", size=9.3)

    # ---- arrows ----
    d.arrow(21, 33, 26, 33, color=P["accent"], lw=2.2)
    d.text(23.5, 35.2, "mTLS +\nBearer Token", size=8, color=P["accent"])

    d.arrow(46, 35, 55, 37, color=P["orange"], lw=2.0)
    d.arrow(46, 32, 77, 36, color=P["orange"], lw=2.0)
    d.text(51.5, 39.2, "X-Scope-OrgID 주입", size=8, color=P["orange"])

    d.arrow(64, 34, 64, 21.5, color=P["violet"], lw=1.8, ls="--")
    d.text(60.5, 27.5, "mTLS", size=8, color=P["violet"], ha="right")
    d.arrow(86, 34, 86, 21.5, color=P["violet"], lw=1.8, ls="--")
    d.text(89.5, 27.5, "mTLS", size=8, color=P["violet"], ha="left")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.4, label="클라이언트 인증(mTLS+토큰)"),
        Line2D([0], [0], color=P["orange"], lw=2.4, label="검증 후 테넌트 헤더 주입"),
        Line2D([0], [0], color=P["violet"], lw=2.4, ls="--", label="컴포넌트 간 mTLS"),
    ], loc="lower left", anchor=(0.005, 0.02))


diagram("36-gateway-auth", draw, w=14, h=7.2, ymax=50)

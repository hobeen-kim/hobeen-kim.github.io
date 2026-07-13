"""CH10 멀티 유저 uid 모델 — uid = userId*100000 + appId (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 공식
    d.box(20, 40, 60, 7, P["gray"], ec=P["accent"], lw=1.6)
    d.text(50, 43.5, "uid = userId × 100000 + appId", size=13,
           weight="bold", color=P["accent"])

    users = [
        ("user 0 (소유자)", 0, P["blue"]),
        ("user 10 (두 번째)", 10, P["purple"]),
    ]
    apps = [
        ("system", "1000"),
        ("com.foo (appId 10123)", "10123"),
    ]

    x0 = [6, 54]
    for (utitle, uid, fc), x in zip(users, x0):
        d.box(x, 6, 40, 28, fc)
        d.text(x + 20, 30.5, utitle, size=10.5, weight="bold")
        for i, (aname, appid) in enumerate(apps):
            y = 22 - i * 8
            d.box(x + 3, y, 34, 6.5, P["chip"])
            realuid = uid * 100000 + int(appid)
            d.text(x + 20, y + 4.4, aname, size=8.8)
            d.text(x + 20, y + 1.8, f"uid = {realuid}", size=8.3, color=P["dim"])

    d.text(50, 2.5, "같은 appId라도 userId가 다르면 서로 다른 uid → 데이터 완전 격리",
           size=8.5, color=P["dim"])


diagram("10-uid-model", draw, w=12, h=6, ymax=48)

"""CH20 §2 뷰어 자격증명 발급 방식 3가지 — Cognito / 백엔드 STS / 백엔드 서명 URL (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    lanes = [
        (37, "A. Cognito\nIdentity Pool", [
            ("브라우저\n(User Pool 로그인)", P["brown"]),
            ("Identity Pool\nGetId · GetCredentialsForIdentity", P["blue"]),
            ("IAM 역할 (공용)\n역할 정책 · ABAC 태그", P["purple"]),
            ("임시 자격증명 1시간\n→ 브라우저가 KVS 직접 호출", P["chip"]),
        ]),
        (21, "B. 백엔드 STS\n+ 세션 정책", [
            ("브라우저\n(앱 로그인 토큰)", P["brown"]),
            ("앱 백엔드\nDB로 시청 권한 확인", P["green"]),
            ("STS AssumeRole\n세션 정책: 채널 ARN · VIEWER", P["purple"]),
            ("임시 자격증명 15분~\n→ 브라우저가 KVS 직접 호출", P["chip"]),
        ]),
        (5, "C. 백엔드\n서명 URL", [
            ("브라우저\n(앱 로그인 토큰)", P["brown"]),
            ("앱 백엔드\n권한 확인 · Endpoint/ICE 조회", P["green"]),
            ("SigV4RequestSigner\nWSS URL 서명 (299초)", P["purple"]),
            ("서명 URL + ICE 서버\n→ 브라우저는 자격증명 없음", P["chip"]),
        ]),
    ]

    x0, w, gap = 14, 18.5, 3.2
    for y, label, chips in lanes:
        d.text(6.5, y + 5, label, size=9, color=P["dim"], weight="bold")
        for i, (text, col) in enumerate(chips):
            x = x0 + i * (w + gap)
            ec = P["accent"] if i == 2 else None
            d.box(x, y, w, 10, col, ec=ec, lw=1.6 if ec else 1.4)
            d.text(x + w / 2, y + 5, text, size=8.2)
            if i < len(chips) - 1:
                d.arrow(x + w, y + 5, x + w + gap, y + 5, color=P["edge"],
                        lw=1.4)

    # 구분선
    for yy in (34, 18):
        d.ax.plot([2, 98], [yy - 0.5, yy - 0.5], color=P["edge"], lw=0.6,
                  ls=(0, (2, 3)), zorder=1)


diagram("20-credential-options", draw, w=13, h=5.6, ymax=49)

"""CH22 §1 주체별 자격증명 경로와 최소 권한 — 디바이스 / 운영자 / 프로비저닝 백엔드 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    heads = [(10, "주체"), (35, "자격증명 경로"), (63, "IAM 역할 · 허용 액션"), (89.5, "Resource")]
    for x, h in heads:
        d.text(x, 51, h, size=9.2, color=P["dim"], weight="bold")

    rows = [
        (41, ("농기계 디바이스", "(X.509 인증서)", P["green"]),
         ("IoT Credentials Provider", "(role alias, mTLS)"),
         ("device-master", "ConnectAsMaster · GetIceServerConfig\nGetSignalingChannelEndpoint · Describe"),
         (r"channel/\${ThingName}/*", "(IAM 정책 변수)")),
        (25, ("운영자 브라우저", "(로그인 사용자)", P["blue"]),
         ("백엔드 STS AssumeRole", "(세션 정책: 채널 1개)"),
         ("operator-viewer", "ConnectAsViewer · GetIceServerConfig\nGetSignalingChannelEndpoint"),
         ("channel/tractor-001/*", "(요청마다 좁힘)")),
        (9, ("프로비저닝 백엔드", "(ECS 태스크 / Lambda)", P["brown"]),
         ("서비스 실행 역할", "(장기 액세스 키 없음)"),
         ("channel-admin", "Create · Delete · Tag · List\nUpdate/DescribeMediaStorageConfiguration"),
         ("channel/* · stream/*", "(aws:RequestTag 조건)")),
    ]
    for y, who, cred, role, res in rows:
        d.box(1, y - 5.5, 18, 11, who[2])
        d.text(10, y + 1.8, who[0], size=9.6, weight="bold")
        d.text(10, y - 2.2, who[1], size=7.8, color=P["dim"])

        d.box(24, y - 5.5, 22, 11, P["chip"])
        d.text(35, y + 1.8, cred[0], size=8.8, weight="bold")
        d.text(35, y - 2.2, cred[1], size=7.8, color=P["dim"])

        d.box(50, y - 5.5, 26, 11, P["purple"])
        d.text(63, y + 2.6, role[0], size=9.2, weight="bold")
        d.text(63, y - 2.0, role[1], size=7.7, color=P["text"])

        d.box(80, y - 5.5, 19, 11, P["gray"], ec=P["accent"], lw=1.4)
        d.text(89.5, y + 1.8, res[0], size=8.4, weight="bold")
        d.text(89.5, y - 2.2, res[1], size=7.6, color=P["dim"])

        d.arrow(19.2, y, 23.8, y, color=P["accent"], lw=1.5)
        d.arrow(46.2, y, 49.8, y, color=P["accent"], lw=1.5)
        d.arrow(76.2, y, 79.8, y, color=P["orange"], lw=1.5)


diagram("22-iam-principals", draw, w=13, h=6.4, ymax=54)

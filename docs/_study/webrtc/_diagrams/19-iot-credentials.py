"""CH19 §4 AWS IoT Credential Provider로 KVS 임시 자격증명 받기 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 디바이스
    d.box(2, 20, 21, 13, P["green"])
    d.text(12.5, 28.6, "디바이스", size=10.5, weight="bold")
    d.text(12.5, 23.6, "X.509 인증서 · 개인키\nThing: tractor-0017", size=8.3,
           color=P["dim"])

    # IoT credentials provider
    d.box(36, 38, 27, 11, P["blue"])
    d.text(49.5, 45.6, "IoT credentials provider", size=10, weight="bold")
    d.text(49.5, 41.3, "{prefix}.credentials.iot\n.{region}.amazonaws.com",
           size=8, color=P["dim"])

    # IoT 정책 칩
    d.box(36, 26.5, 27, 8, P["chip"], ec=P["edge"], lw=1.0)
    d.text(49.5, 30.5, "IoT 정책 (인증서에 부착)\niot:AssumeRoleWithCertificate",
           size=8, color=P["dim"])
    d.ax.plot([49.5, 49.5], [34.5, 38], color=P["edge"], lw=1.0, ls=":",
              zorder=1)

    # role alias → IAM role
    d.box(74, 38, 24, 11, P["purple"])
    d.text(86, 45.6, "role alias → IAM 역할", size=10, weight="bold")
    d.text(86, 41.3, "신뢰: credentials.iot\n.amazonaws.com", size=8,
           color=P["dim"])

    # KVS
    d.box(74, 4, 24, 11, P["brown"])
    d.text(86, 11.4, "KVS 시그널링", size=10, weight="bold")
    d.text(86, 7.2, "Describe · GetEndpoint\nGetIceServerConfig · ConnectAsMaster",
           size=7.8, color=P["dim"])

    # IAM 정책 칩
    d.box(36, 1.5, 31, 8.5, P["chip"], ec=P["orange"], lw=1.0)
    d.text(51.5, 5.75, "역할의 IAM 정책 리소스\nchannel/${credentials-iot:ThingName}/*",
           size=8, color=P["orange"])
    d.ax.plot([67, 74], [5.75, 5.75], color=P["orange"], lw=1.0, ls=":",
              zorder=1)

    # ① 요청
    d.arrow(23, 31, 36, 42, color=P["accent"])
    d.text(14, 40.5, "① mTLS GET\n/role-aliases/{alias}/credentials\n"
           "x-amzn-iot-thingname 헤더", size=7.8, color=P["accent"])

    # ② assume
    d.arrow(63, 45, 74, 45, color=P["violet"])
    d.text(68.5, 47.4, "② AssumeRole", size=7.8, color=P["violet"])

    # ③ 응답
    d.arrow(36, 39.5, 23, 28.5, color=P["orange"], ls="--")
    d.text(24.5, 22.5, "③ accessKeyId · secretAccessKey\n    sessionToken · expiration",
           size=7.8, color=P["orange"], ha="left")

    # ④ SigV4
    d.arrow(23, 21.5, 74, 12.5, color=P["accent"])
    d.ax.text(55, 17.6, "④ SigV4 서명 요청 (만료 전 provider가 재발급)",
              fontsize=7.8, color=P["accent"], ha="center", va="center",
              zorder=6, bbox=dict(facecolor=P["bg"], edgecolor="none",
                                  pad=1.2))


diagram("19-iot-credentials", draw, w=12.5, h=5.6, ymax=51)

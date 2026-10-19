"""CH20 §4 시그널링 채널 프로비저닝 상태 머신 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def state(x, y, w, h, name, sub, col, ec=None):
        d.box(x, y, w, h, col, ec=ec, lw=1.6 if ec else 1.4)
        d.text(x + w / 2, y + h / 2 + 1.4, name, size=10, weight="bold")
        d.text(x + w / 2, y + h / 2 - 1.8, sub, size=7.8, color=P["dim"])

    # 1행
    state(3, 37, 21, 9, "REQUESTED", "디바이스 등록 이벤트", P["gray"])
    state(40, 37, 21, 9, "CREATING", "ARN 저장 · 생성 중", P["blue"])
    state(77, 37, 21, 9, "ACTIVE", "뷰어 세션 발급 가능", P["green"],
          ec=P["accent"])
    # 2행
    state(40, 20.5, 21, 9, "RETRY", "백오프 후 재시도", P["chip"])
    # 3행
    state(77, 3, 21, 9, "DELETING", "삭제 요청됨", P["brown"])
    state(40, 3, 21, 9, "DELETED", "행 보존 · 재등록 가능", P["gray"])

    def lbl(x, y, s, color, ha="center"):
        d.ax.text(x, y, s, fontsize=7.9, color=color, ha=ha, va="center",
                  zorder=6, bbox=dict(facecolor=P["bg"], edgecolor="none",
                                      pad=1.0))

    # 전이
    d.arrow(24, 41.5, 40, 41.5, color=P["accent"])
    lbl(32, 47.5, "Describe → 없으면\nCreateSignalingChannel", P["accent"])

    d.arrow(61, 41.5, 77, 41.5, color=P["accent"])
    lbl(69, 47.5, "Describe 폴링\nChannelStatus=ACTIVE", P["accent"])

    d.arrow(47, 37, 47, 29.5, color=P["orange"])
    lbl(46, 33.2, "스로틀·오류", P["orange"], ha="right")
    d.arrow(54, 29.5, 54, 37, color=P["dim"], ls="--")
    lbl(55, 33.2, "Describe부터 다시", P["dim"], ha="left")

    d.arrow(87.5, 37, 87.5, 12, color=P["violet"])
    lbl(86.5, 24.5, "디바이스 폐기\n인증서 비활성화 →\nDeleteSignalingChannel",
        P["violet"], ha="right")

    d.arrow(77, 7.5, 61, 7.5, color=P["violet"])
    lbl(69, 13.3, "Describe →\nResourceNotFound", P["violet"])

    # DB 칩
    d.box(3, 11, 24, 17, P["chip"], ec=P["edge"], lw=1.0)
    d.text(5, 25, "device_video_channel", size=8.5, weight="bold", ha="left")
    d.text(5, 22, "device_id (PK)\nchannel_name (= thing 이름)\nchannel_arn\n"
           "channel_version\nstatus · attempts\nlast_error · updated_at",
           size=7.8, color=P["dim"], ha="left", va="top")


diagram("20-provisioning", draw, w=12.5, h=6, ymax=52)

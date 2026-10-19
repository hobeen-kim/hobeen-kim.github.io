"""CH15 §1 getStats() 리포트 객체 관계 — id 참조로 엮인 통계 그래프 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def label(x, y, s, color):
        d.ax.text(x, y, s, fontsize=8.5, color=color, ha="center",
                  va="center", zorder=6,
                  bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.2))

    def row_title(y, s):
        d.text(3, y, s, size=9, color=P["dim"], ha="left", style="italic")

    # 1행: 연결 경로
    row_title(53.2, "연결 경로")
    d.box(3, 41, 20, 9, P["gray"])
    d.text(13, 45.5, "transport\n(dtlsState · iceState)", size=9.5)
    d.box(33, 41, 27, 9, P["blue"], ec=P["accent"], lw=1.8)
    d.text(46.5, 45.5, "candidate-pair\n(currentRoundTripTime)", size=9.5)
    d.box(71, 46, 26, 6.5, P["chip"])
    d.text(84, 49.25, "local-candidate (relay?)", size=9.5)
    d.box(71, 37.5, 26, 6.5, P["chip"])
    d.text(84, 40.75, "remote-candidate", size=9.5)
    d.arrow(23, 45.5, 33, 45.5)
    label(28, 47.6, "selected\nCandidatePairId", P["dim"])
    d.arrow(60, 47, 71, 49.25)
    label(65.5, 50.6, "localCandidateId", P["dim"])
    d.arrow(60, 44, 71, 40.75)
    label(65.5, 40.0, "remoteCandidateId", P["dim"])

    # 2행: 보내는 쪽
    row_title(33.2, "보내는 쪽 (상대가 보낸 RTCP RR 반영)")
    d.box(3, 20.5, 20, 9, P["gray"])
    d.text(13, 25, "media-source\n(audioLevel · width)", size=9.5)
    d.box(33, 20.5, 27, 9, P["green"], ec=P["accent"], lw=1.8)
    d.text(46.5, 25, "outbound-rtp\n(qualityLimitationReason)", size=9.5)
    d.box(71, 20.5, 26, 9, P["purple"])
    d.text(84, 25, "remote-inbound-rtp\n(roundTripTime · fractionLost)",
           size=9.5)
    d.arrow(33, 25, 23, 25)
    label(28, 27.2, "mediaSourceId", P["dim"])
    d.arrow(60, 25, 71, 25, style="<|-|>", color=P["orange"])
    label(65.5, 27.2, "remoteId ↔ localId", P["orange"])

    # 3행: 받는 쪽
    row_title(13.2, "받는 쪽 (상대가 보낸 RTCP SR 반영)")
    d.box(3, 1, 20, 9, P["gray"])
    d.text(13, 5.5, "codec\n(mimeType · sdpFmtpLine)", size=9.5)
    d.box(33, 1, 27, 9, P["brown"], ec=P["accent"], lw=1.8)
    d.text(46.5, 5.5, "inbound-rtp\n(jitter · packetsLost)", size=9.5)
    d.box(71, 1, 26, 9, P["purple"])
    d.text(84, 5.5, "remote-outbound-rtp\n(remoteTimestamp)", size=9.5)
    d.arrow(33, 5.5, 23, 5.5)
    label(28, 7.7, "codecId", P["dim"])
    d.arrow(60, 5.5, 71, 5.5, style="<|-|>", color=P["orange"])
    label(65.5, 7.7, "remoteId ↔ localId", P["orange"])


diagram("15-stats-graph", draw, w=13, h=7.2, ymax=55)

"""CH18 §1 KVS 시그널링 API가 호출되는 엔드포인트 계층 — 컨트롤 플레인 / 채널 HTTPS / 채널 WSS / WEBRTC (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 호출 주체 (왼쪽)
    callers = [(44, "백엔드\n(프로비저닝)", P["gray"]),
               (27, "디바이스\n(Master)", P["green"]),
               (10, "브라우저\n(Viewer)", P["blue"])]
    for y, name, col in callers:
        d.box(2, y - 4, 14, 8, col)
        d.text(9, y, name, size=8.5, weight="bold")

    # 엔드포인트 계층 (오른쪽)
    layers = [
        (46, "컨트롤 플레인", "kinesisvideo.{region}.amazonaws.com",
         "Create / Describe / List / Update / Delete SignalingChannel\n"
         "Tag · Untag · ListTags · GetSignalingChannelEndpoint", P["gray"]),
        (33, "채널 HTTPS 엔드포인트", "r-xxxxxxxx.kinesisvideo.{region}…",
         "GetIceServerConfig · SendAlexaOfferToMaster", P["purple"]),
        (20, "채널 WSS 엔드포인트", "m-xxxxxxxx.kinesisvideo.{region}…",
         "ConnectAsMaster · ConnectAsViewer\nSDP_OFFER · SDP_ANSWER · ICE_CANDIDATE",
         P["purple"]),
        (7, "채널 WEBRTC 엔드포인트", "저장(ingestion) 설정 채널만",
         "JoinStorageSession · JoinStorageSessionAsViewer (21장)", P["brown"]),
    ]
    for y, name, host, apis, col in layers:
        d.box(38, y - 5, 60, 10, col)
        d.text(40, y + 2.6, name, size=9, weight="bold", ha="left")
        d.text(96, y + 2.6, host, size=7.5, color=P["dim"], ha="right")
        d.text(40, y - 1.6, apis, size=8, ha="left")

    # 호출 화살표
    a = dict(lw=1.3)
    d.arrow(16, 45, 38, 46, color=P["accent"], **a)
    d.arrow(16, 28.5, 38, 44, color=P["accent"], **a)
    d.arrow(16, 27, 38, 33, color=P["accent"], **a)
    d.arrow(16, 25.5, 38, 21, color=P["violet"], **a)
    d.arrow(16, 11.5, 38, 42.5, color=P["accent"], ls="--", **a)
    d.arrow(16, 10.5, 38, 31.5, color=P["accent"], ls="--", **a)
    d.arrow(16, 9.5, 38, 19, color=P["violet"], **a)
    d.text(27, 3.5, "점선: 백엔드가 대신 호출해\n결과만 넘겨줄 수 있는 구간",
           size=7.5, color=P["dim"])


diagram("18-endpoint-layers", draw, w=13, h=6.4, ymax=53)

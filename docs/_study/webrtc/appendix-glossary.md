---
title: "용어집"
description: "WebRTC 스터디 본문에 등장한 핵심 용어를 API, 시그널링, NAT·ICE, 미디어, 품질 제어, 보안, DataChannel, 아키텍처, 표준, AWS 카테고리별로 정리한 레퍼런스."
date: 2026-10-19
tags: [WebRTC, Glossary]
prev: /study/webrtc/25-capstone-farm-platform
next: /study/webrtc/appendix-references
---

# 용어집

본문에 등장한 핵심 용어를 카테고리별로 정리한다. 기술 용어는 원문 표기를 유지하고, 마지막 열은 해당 용어를 처음 다루는 챕터이다.

## WebRTC API

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| getUserMedia | 카메라·마이크 접근 권한을 요청하고 MediaStream을 돌려주는 브라우저 API. 권한은 사용자 동의가 있어야 부여된다. | [02장](/study/webrtc/02-webrtc-api) |
| MediaStream | 여러 MediaStreamTrack을 묶은 컨테이너. 하나의 영상·음성 묶음을 PeerConnection에 넘길 때 쓴다. | [02장](/study/webrtc/02-webrtc-api) |
| MediaStreamTrack | 오디오 또는 비디오 한 줄기를 나타내는 객체. Sender에 붙이거나 replaceTrack으로 교체할 수 있다. | [02장](/study/webrtc/02-webrtc-api) |
| RTCPeerConnection | 피어 간 연결의 수립·미디어 송수신·상태를 관리하는 WebRTC의 중심 객체. | [02장](/study/webrtc/02-webrtc-api) |
| RTCRtpTransceiver | 하나의 m-line에 대응하는 Sender와 Receiver의 쌍. direction으로 송수신 방향을 정한다. | [02장](/study/webrtc/02-webrtc-api) |
| RTCRtpSender / RTCRtpReceiver | 트랙을 RTP로 보내고 받는 객체. Sender의 getParameters·setParameters로 비트레이트와 해상도 배율을 조절한다. | [02장](/study/webrtc/02-webrtc-api) |
| RTCDataChannel | PeerConnection 위에서 임의의 바이너리·텍스트 메시지를 주고받는 양방향 채널. | [02장](/study/webrtc/02-webrtc-api) |
| addTransceiver | 트랙 없이도 m-line과 방향을 미리 선언하는 API. 수신 전용(recvonly) 뷰어를 만들 때 쓴다. | [02장](/study/webrtc/02-webrtc-api) |
| replaceTrack | 재협상 없이 Sender가 보내는 트랙만 바꾸는 메서드. 카메라 전환에 쓴다. | [02장](/study/webrtc/02-webrtc-api) |
| getStats | 연결의 RTP·후보 쌍·코덱 통계를 리포트 형태로 돌려주는 API. 품질 모니터링의 기본 수단이다. | [02장](/study/webrtc/02-webrtc-api) |
| signalingState | Offer/Answer 진행 단계를 나타내는 상태(stable, have-local-offer 등). | [02장](/study/webrtc/02-webrtc-api) |
| connectionState | ICE와 DTLS를 합친 연결 전체 상태(new, connecting, connected, failed 등). | [02장](/study/webrtc/02-webrtc-api) |

## 시그널링·SDP

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| 시그널링(Signaling) | 피어끼리 SDP와 ICE 후보를 교환하도록 중개하는 과정. WebRTC는 전송 방식을 표준화하지 않았다. | [03장](/study/webrtc/03-signaling) |
| JSEP | JavaScript Session Establishment Protocol. 브라우저가 Offer/Answer 협상을 API로 다루는 모델(RFC 9429). | [04장](/study/webrtc/04-sdp-jsep) |
| SDP | Session Description Protocol. 미디어 종류, 코덱, ICE 정보, 지문 등 세션 능력을 기술하는 텍스트 형식. | [04장](/study/webrtc/04-sdp-jsep) |
| Offer / Answer | 협상을 시작하는 쪽이 Offer SDP를, 응답하는 쪽이 Answer SDP를 보내 합의하는 모델. | [04장](/study/webrtc/04-sdp-jsep) |
| m-line | SDP에서 미디어 하나(오디오·비디오·application)를 선언하는 `m=` 줄. | [04장](/study/webrtc/04-sdp-jsep) |
| mid | m-line을 식별하는 `a=mid` 값. BUNDLE과 트랜시버 매칭에 쓰인다. | [04장](/study/webrtc/04-sdp-jsep) |
| BUNDLE | 여러 m-line의 미디어를 하나의 전송 5-tuple로 묶는 방식. 포트와 ICE 연결 수를 줄인다. | [04장](/study/webrtc/04-sdp-jsep) |
| rtcp-mux | RTP와 RTCP를 같은 포트로 다중화하는 설정. | [04장](/study/webrtc/04-sdp-jsep) |
| rtpmap / fmtp | payload type에 코덱 이름·클럭레이트를 매핑하는 줄과, 코덱별 파라미터를 적는 줄. | [04장](/study/webrtc/04-sdp-jsep) |
| extmap | RTP 헤더 확장의 ID와 URI를 매핑하는 `a=extmap` 줄. | [04장](/study/webrtc/04-sdp-jsep) |
| Perfect Negotiation | 양쪽이 동시에 Offer를 보내는 glare를 polite/impolite 역할로 해소하는 재협상 패턴. | [04장](/study/webrtc/04-sdp-jsep) |
| glare | 양쪽이 동시에 Offer를 보내 충돌하는 상황. | [04장](/study/webrtc/04-sdp-jsep) |
| rollback | 로컬 Offer를 되돌려 stable 상태로 복귀하는 JSEP 동작. | [04장](/study/webrtc/04-sdp-jsep) |
| SDP munging | SDP 문자열을 직접 편집하는 방식. 브라우저 버전에 따라 깨질 수 있어 가급적 API로 대체한다. | [04장](/study/webrtc/04-sdp-jsep) |
| setCodecPreferences | 트랜시버의 코덱 우선순위를 API로 지정하는 메서드. SDP munging의 대안이다. | [04장](/study/webrtc/04-sdp-jsep) |
| Unified Plan | m-line 하나당 트랙 하나를 대응시키는 현행 SDP 구조. 과거의 Plan B를 대체했다. | [04장](/study/webrtc/04-sdp-jsep) |

## NAT·ICE·STUN·TURN

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| NAT | 사설 주소를 공인 주소·포트로 변환하는 장치. 외부에서 먼저 들어오는 패킷을 막아 P2P를 어렵게 한다. | [05장](/study/webrtc/05-nat-stun) |
| CGNAT | 통신사가 여러 가입자에 공유 공인 주소를 쓰게 하는 NAT(RFC 6888). LTE 디바이스에서 흔하다. | [05장](/study/webrtc/05-nat-stun) |
| Symmetric NAT | 목적지마다 다른 외부 포트를 할당하는 NAT. 홀펀칭이 사실상 실패해 TURN이 필요하다. | [05장](/study/webrtc/05-nat-stun) |
| STUN | NAT 바깥에서 보이는 자신의 주소를 알려주는 서버·프로토콜(RFC 8489). | [05장](/study/webrtc/05-nat-stun) |
| XOR-MAPPED-ADDRESS | STUN 응답에 담긴, 서버가 본 클라이언트의 공인 주소 속성. | [05장](/study/webrtc/05-nat-stun) |
| UDP 홀펀칭 | 양쪽이 동시에 상대 주소로 패킷을 보내 NAT에 매핑을 만들어 직접 통신하는 기법. | [05장](/study/webrtc/05-nat-stun) |
| ICE | 후보 주소를 모아 연결 가능한 경로를 찾고 선택하는 프레임워크(RFC 8445). | [06장](/study/webrtc/06-ice) |
| Host 후보 | 단말의 로컬 네트워크 인터페이스 주소로 만든 후보. | [06장](/study/webrtc/06-ice) |
| srflx 후보 | STUN으로 알아낸 NAT 바깥 주소(server reflexive)로 만든 후보. | [06장](/study/webrtc/06-ice) |
| prflx 후보 | 연결 확인 도중 상대가 보낸 요청의 출발 주소에서 발견되는 후보(peer reflexive). | [06장](/study/webrtc/06-ice) |
| relay 후보 | TURN 서버가 할당한 릴레이 주소로 만든 후보. | [06장](/study/webrtc/06-ice) |
| Candidate pair | 로컬 후보와 원격 후보의 조합. ICE는 쌍마다 connectivity check를 수행한다. | [06장](/study/webrtc/06-ice) |
| Nomination | 검사에 성공한 후보 쌍 중 실제 사용할 쌍을 확정하는 단계. | [06장](/study/webrtc/06-ice) |
| Trickle ICE | 후보를 수집되는 대로 점진적으로 보내 연결 수립 시간을 줄이는 방식(RFC 8838). | [06장](/study/webrtc/06-ice) |
| ICE restart | 네트워크 변경이나 실패 후 새 ufrag·pwd로 후보를 다시 수집하는 복구 절차. | [06장](/study/webrtc/06-ice) |
| mDNS 후보 | 로컬 IP 노출을 막으려고 host 후보 주소를 임의의 `.local` 이름으로 대체한 후보. | [06장](/study/webrtc/06-ice) |
| ICE-lite | 공인 주소를 가진 서버가 후보 수집 없이 응답만 하는 경량 ICE 구현. | [06장](/study/webrtc/06-ice) |
| TURN | 피어 간 직접 연결이 불가능할 때 트래픽을 중계하는 서버·프로토콜(RFC 8656). | [07장](/study/webrtc/07-turn) |
| Allocate / Refresh | TURN 클라이언트가 릴레이 주소를 할당받고 수명을 연장하는 요청. | [07장](/study/webrtc/07-turn) |
| ChannelBind | TURN 릴레이에서 헤더가 작은 채널 데이터로 전송하도록 피어를 채널 번호에 묶는 요청. | [07장](/study/webrtc/07-turn) |
| coturn | 가장 널리 쓰이는 오픈소스 TURN/STUN 서버. | [07장](/study/webrtc/07-turn) |
| iceTransportPolicy | `relay`로 두면 릴레이 후보만 사용하도록 강제하는 PeerConnection 설정. | [07장](/study/webrtc/07-turn) |

## 미디어·RTP·코덱

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| RTP | 미디어 패킷에 시퀀스와 타임스탬프를 붙여 실시간 전송하는 프로토콜(RFC 3550). | [08장](/study/webrtc/08-rtp-codecs) |
| RTCP | RTP 세션의 전송 통계와 피드백을 주고받는 제어 프로토콜. | [08장](/study/webrtc/08-rtp-codecs) |
| SSRC | RTP 스트림 하나를 식별하는 32비트 값. | [08장](/study/webrtc/08-rtp-codecs) |
| Payload Type | RTP 패킷의 코덱 종류를 가리키는 번호. SDP의 rtpmap이 의미를 정의한다. | [08장](/study/webrtc/08-rtp-codecs) |
| Sender Report / Receiver Report | RTCP로 송신 통계와 수신 품질(손실·지터)을 알리는 보고. | [08장](/study/webrtc/08-rtp-codecs) |
| RTX | 손실된 패킷을 별도 SSRC·payload type으로 재전송하는 방식(RFC 4588). | [08장](/study/webrtc/08-rtp-codecs) |
| abs-send-time | 패킷 송신 시각을 담는 RTP 헤더 확장. 대역폭 추정에 쓰인다. | [08장](/study/webrtc/08-rtp-codecs) |
| transport-cc | 패킷별 도착 시각을 피드백하는 헤더 확장·RTCP. TWCC의 기반이다. | [08장](/study/webrtc/08-rtp-codecs) |
| VP8 / VP9 / AV1 | 오픈 비디오 코덱 계열. AV1은 압축 효율이 높지만 인코딩 부하가 크다. | [08장](/study/webrtc/08-rtp-codecs) |
| H.264 | 하드웨어 인코더가 널리 지원하는 비디오 코덱. profile-level-id로 능력을 협상한다. | [08장](/study/webrtc/08-rtp-codecs) |
| profile-level-id | H.264의 프로파일·레벨을 SDP fmtp에 16진수로 표시한 파라미터. | [08장](/study/webrtc/08-rtp-codecs) |
| Opus | WebRTC 필수 오디오 코덱. 가변 비트레이트와 FEC를 지원한다(RFC 7587). | [08장](/study/webrtc/08-rtp-codecs) |
| NAL unit / FU-A | H.264 비트스트림의 전송 단위와, MTU보다 큰 NAL을 쪼개 전송하는 패킷화 방식. | [08장](/study/webrtc/08-rtp-codecs) |
| 키프레임(IDR) | 다른 프레임 참조 없이 독립 디코딩되는 프레임. 새 시청자나 손실 복구에 필요하다. | [08장](/study/webrtc/08-rtp-codecs) |
| 지터 버퍼 | 도착 시각의 흔들림을 흡수해 재생을 매끄럽게 하는 수신 버퍼. 크기만큼 지연이 늘어난다. | [08장](/study/webrtc/08-rtp-codecs) |
| libwebrtc | Google이 공개한 WebRTC 참조 구현. Chrome이 사용하며 네이티브 빌드도 가능하다. | [08장](/study/webrtc/08-rtp-codecs) |

## 품질 제어

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| NACK | 손실된 RTP 패킷의 재전송을 요청하는 RTCP 피드백. | [09장](/study/webrtc/09-quality-latency) |
| PLI / FIR | 키프레임 재전송을 요청하는 피드백. PLI는 손실 복구, FIR은 강제 요청에 쓴다. | [09장](/study/webrtc/09-quality-latency) |
| FEC | 중복 정보를 함께 보내 재전송 없이 손실을 복구하는 기법. ULPFEC·FlexFEC·RED가 있다. | [09장](/study/webrtc/09-quality-latency) |
| GCC | Google Congestion Control. 지연 기반과 손실 기반 추정을 결합한 혼잡 제어 알고리즘. | [09장](/study/webrtc/09-quality-latency) |
| TWCC | Transport-Wide Congestion Control. 수신 측이 패킷별 도착 시각을 피드백해 송신 측이 대역폭을 추정하게 한다. | [08장](/study/webrtc/08-rtp-codecs) |
| REMB | 수신 측이 추정한 가용 대역폭을 알려주는 RTCP 메시지. 현재는 TWCC가 주로 쓰인다. | [08장](/study/webrtc/08-rtp-codecs) |
| maxBitrate | Sender 인코딩 파라미터에서 비트레이트 상한을 지정하는 값. | [02장](/study/webrtc/02-webrtc-api) |
| scaleResolutionDownBy | 전송 해상도를 배율로 낮추는 인코딩 파라미터. | [02장](/study/webrtc/02-webrtc-api) |
| degradationPreference | 대역폭 부족 시 해상도와 프레임레이트 중 무엇을 희생할지 정하는 설정. | [02장](/study/webrtc/02-webrtc-api) |
| qualityLimitationReason | outbound-rtp 통계에서 화질이 제한된 원인(cpu, bandwidth 등)을 알려주는 필드. | [09장](/study/webrtc/09-quality-latency) |
| glass-to-glass 지연 | 카메라 렌즈에서 운영자 화면까지의 전체 지연. 캡처·인코딩·네트워크·지터버퍼·디코드·렌더로 분해한다. | [01장](/study/webrtc/01-why-webrtc) |
| jitterBufferTarget | 수신 측 지터 버퍼의 목표 지연을 힌트로 지정하는 속성. | [02장](/study/webrtc/02-webrtc-api) |

## 보안

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| DTLS | UDP 위에서 TLS와 유사한 핸드셰이크를 수행하는 프로토콜. WebRTC에서 키 교환에 쓴다. | [10장](/study/webrtc/10-dtls-srtp) |
| SRTP | RTP 페이로드를 암호화하고 인증하는 프로토콜. | [10장](/study/webrtc/10-dtls-srtp) |
| DTLS-SRTP | DTLS 핸드셰이크에서 SRTP 키를 도출해 미디어를 암호화하는 방식(RFC 5764). | [10장](/study/webrtc/10-dtls-srtp) |
| fingerprint | SDP에 담기는 인증서 해시. DTLS 상대 인증서를 검증하는 기준이다. | [10장](/study/webrtc/10-dtls-srtp) |
| generateCertificate | RTCPeerConnection이 사용할 인증서를 미리 생성하는 API. | [10장](/study/webrtc/10-dtls-srtp) |
| E2EE | SFU도 내용을 볼 수 없게 종단 간 암호화를 얹는 방식. Insertable Streams로 구현한다. | [12장](/study/webrtc/12-topology-sfu) |
| SFrame | 프레임 단위로 암호화하는 E2EE 포맷(RFC 9605). | [10장](/study/webrtc/10-dtls-srtp) |
| Insertable Streams | 인코딩된 프레임을 가로채 변환하는 API(Encoded Transform). E2EE 구현의 기반이다. | [12장](/study/webrtc/12-topology-sfu) |

## DataChannel

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| SCTP | 메시지 지향 전송 프로토콜. WebRTC DataChannel은 DTLS 위의 SCTP를 사용한다. | [11장](/study/webrtc/11-datachannel) |
| ordered / maxRetransmits / maxPacketLifeTime | DataChannel의 순서 보장과 재전송 횟수·시간 제한 옵션. 신뢰성 수준을 정한다. | [11장](/study/webrtc/11-datachannel) |
| negotiated | SDP 협상 없이 양쪽이 id를 합의해 채널을 만드는 옵션. | [11장](/study/webrtc/11-datachannel) |
| bufferedAmount | DataChannel 송신 큐에 쌓인 바이트 수. 흐름 제어에 쓴다. | [11장](/study/webrtc/11-datachannel) |
| 데드맨 스위치 | 제어 입력이 끊기면 장비를 안전 상태로 전환하는 장치. | [11장](/study/webrtc/11-datachannel) |
| 워치독 | 주기적 신호가 없으면 장애로 판단해 조치하는 감시 로직. | [11장](/study/webrtc/11-datachannel) |

## 아키텍처

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| Mesh | 모든 참가자가 서로 직접 연결하는 구조. 참가자 수에 비례해 업링크가 늘어난다. | [12장](/study/webrtc/12-topology-sfu) |
| SFU | Selective Forwarding Unit. 송신자의 스트림을 디코딩 없이 수신자들에게 전달하는 서버. | [12장](/study/webrtc/12-topology-sfu) |
| MCU | Multipoint Control Unit. 여러 스트림을 서버에서 디코딩·합성해 하나로 내보내는 서버. | [12장](/study/webrtc/12-topology-sfu) |
| Simulcast | 한 송신자가 해상도가 다른 여러 스트림을 동시에 보내는 방식. RID로 구분한다. | [12장](/study/webrtc/12-topology-sfu) |
| SVC | Scalable Video Coding. 하나의 스트림에 계층을 담아 수신자별로 일부만 전달하는 방식. | [12장](/study/webrtc/12-topology-sfu) |
| 캐스케이딩 SFU | 여러 SFU를 연결해 규모와 지역을 확장하는 구조. | [12장](/study/webrtc/12-topology-sfu) |
| mediasoup / Janus / LiveKit | 대표적인 오픈소스 SFU. | [12장](/study/webrtc/12-topology-sfu) |
| Pion | Go로 작성된 WebRTC 구현. 서버와 디바이스 양쪽에서 쓴다. | [13장](/study/webrtc/13-native-webrtc) |
| GStreamer webrtcbin | GStreamer의 WebRTC 엘리먼트. 하드웨어 인코더 파이프라인과 연결해 디바이스 송신에 쓴다. | [13장](/study/webrtc/13-native-webrtc) |
| V4L2 / NVENC | 리눅스 비디오 캡처·인코딩 인터페이스와 NVIDIA의 하드웨어 인코더. | [13장](/study/webrtc/13-native-webrtc) |

## 표준 (WHIP/WHEP)

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| WHIP | WebRTC-HTTP Ingestion Protocol. HTTP POST 한 번으로 SDP를 교환해 미디어를 올리는 표준(RFC 9725). | [14장](/study/webrtc/14-whip-whep) |
| WHEP | WebRTC-HTTP Egress Protocol. WHIP과 대칭으로 미디어를 받는 HTTP 시그널링 드래프트. | [14장](/study/webrtc/14-whip-whep) |
| HLS / LL-HLS | HTTP 세그먼트 기반 스트리밍과 지연을 줄인 변형. WebRTC보다 지연이 크다. | [01장](/study/webrtc/01-why-webrtc) |
| RTMP | 방송 인코더가 서버로 영상을 올릴 때 널리 쓰던 프로토콜. | [01장](/study/webrtc/01-why-webrtc) |

## AWS (KVS·Chime SDK·IVS·IoT)

| 용어 | 설명 | 처음 등장 |
|---|---|---|
| Signaling Channel | KVS WebRTC에서 Master와 Viewer가 SDP·ICE 후보를 주고받는 관리형 시그널링 채널. | [17장](/study/webrtc/17-kvs-architecture) |
| Master / Viewer | KVS 채널에서 영상을 보내는 쪽(디바이스)과 받는 쪽(운영자)의 역할. | [17장](/study/webrtc/17-kvs-architecture) |
| GetSignalingChannelEndpoint | 채널의 WSS·HTTPS 엔드포인트를 조회하는 API. | [18장](/study/webrtc/18-kvs-signaling-api) |
| GetIceServerConfig | 관리형 TURN 서버 URI와 임시 자격증명을 받는 API. | [18장](/study/webrtc/18-kvs-signaling-api) |
| SigV4 | AWS 요청 서명 방식. KVS 시그널링은 서명된 WSS URL로 접속한다. | [18장](/study/webrtc/18-kvs-signaling-api) |
| KVS Producer SDK | 디바이스 영상을 KVS Video Streams로 올리는 SDK. WebRTC SDK와 별개다. | [17장](/study/webrtc/17-kvs-architecture) |
| JoinStorageSession | WebRTC 연결로 들어온 영상을 Video Stream에 저장하는 세션 참여 API. | [21장](/study/webrtc/21-kvs-ingestion-storage) |
| Credential Provider | IoT 인증서로 임시 AWS 자격증명을 발급하는 AWS IoT 엔드포인트. | [19장](/study/webrtc/19-kvs-c-sdk) |
| Role alias | Credential Provider가 가정할 IAM 역할을 가리키는 이름. | [19장](/study/webrtc/19-kvs-c-sdk) |
| AssumeRole | STS로 임시 자격증명을 얻는 API. 뷰어 발급 시 세션 정책으로 채널 범위를 제한한다. | [20장](/study/webrtc/20-kvs-viewer-backend) |
| Amazon Chime SDK | SFU 기반 회의용 AWS 서비스. 서버가 Meeting과 Attendee를 만들고 클라이언트 SDK가 접속한다. | [23장](/study/webrtc/23-chime-sdk) |
| Media Pipelines | Chime SDK 회의의 녹화·라이브 스트림 연동 등을 처리하는 기능. | [23장](/study/webrtc/23-chime-sdk) |
| Amazon IVS Real-Time | Stage에 참가자가 publish/subscribe하는 SFU 기반 AWS 서비스. | [24장](/study/webrtc/24-ivs-real-time) |
| Stage / Participant Token | IVS Real-Time의 세션 단위와, 참가자 권한을 담아 서버가 발급하는 접속 토큰. | [24장](/study/webrtc/24-ivs-real-time) |
| Composition | IVS에서 서버 측으로 여러 참가자 영상을 합성해 내보내는 기능. | [24장](/study/webrtc/24-ivs-real-time) |
| AWS IoT Core / MQTT | 디바이스 인증·메시징 서비스와 그 경량 프로토콜. 제어·텔레메트리 채널로 DataChannel과 역할을 나눈다. | [25장](/study/webrtc/25-capstone-farm-platform) |

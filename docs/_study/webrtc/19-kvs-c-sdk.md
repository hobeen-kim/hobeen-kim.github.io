---
title: "디바이스 측 구현: KVS C SDK"
description: "amazon-kinesis-video-streams-webrtc-sdk-c의 구조·의존성·빌드 옵션, kvsWebrtcClientMaster 샘플이 자격증명에서 writeFrame까지 가는 흐름, GStreamer appsink로 하드웨어 인코더 출력을 넘기는 구조, AWS IoT Credential Provider로 인증서 기반 임시 자격증명을 받는 방법, 크로스 컴파일·메모리·로그 레벨 운영 팁을 다룬다."
date: 2026-10-19
tags: [WebRTC, AWS, KVS, Embedded, GStreamer, IoT]
prev: /study/webrtc/18-kvs-signaling-api
next: /study/webrtc/20-kvs-viewer-backend
---

# 디바이스 측 구현: KVS C SDK

::: info 학습 목표
- KVS C SDK 저장소가 어떤 라이브러리와 서드파티 의존성으로 이뤄져 있는지, 주요 CMake 옵션이 무엇을 바꾸는지 설명할 수 있다.
- `kvsWebrtcClientMaster` 샘플이 자격증명 → 시그널링 클라이언트 → 오퍼 수신 → PeerConnection → `writeFrame`으로 이어지는 흐름을 C API 단위로 따라갈 수 있다.
- GStreamer `appsink`로 하드웨어 인코더 출력을 SDK에 넘기는 구조와, 뷰어 수만큼 늘어나는 비용을 이해한다.
- AWS IoT Credential Provider와 role alias로 디바이스에 장기 키 없이 임시 자격증명을 주고, Thing 이름 = 채널 이름으로 권한을 묶을 수 있다.
- 크로스 컴파일·메모리·로그 레벨을 조정해 임베디드 보드에 SDK를 올리고 현장에서 디버깅할 수 있다.
:::

[13장](/study/webrtc/13-native-webrtc)에서 브라우저 밖 WebRTC의 선택지로 libwebrtc·Pion·GStreamer `webrtcbin`·aiortc를 비교하고, KVS C SDK는 예고만 했다. 이 장은 그 KVS C SDK(`awslabs/amazon-kinesis-video-streams-webrtc-sdk-c`)로 농기계 카메라를 KVS 시그널링 채널의 master로 붙이는 방법을 다룬다. [17장](/study/webrtc/17-kvs-architecture)·[18장](/study/webrtc/18-kvs-signaling-api)에서 본 `DescribeSignalingChannel` → `GetSignalingChannelEndpoint` → `GetIceServerConfig` → `ConnectAsMaster` 호출을 SDK가 상태 머신으로 감싸 준다는 점이 다른 선택지와 가장 큰 차이다.

기준은 2026-10 현재 최신 릴리스 <strong>v1.20.0(2026-08-18)</strong>과 기본 브랜치 `main`이다. 샘플 디렉터리는 `samples/common`, `samples/p2p`, `samples/webrtcstorage`로 나뉘어 있다. 예전 블로그 글에 나오는 `samples/Common.c` 경로는 지금 `samples/common/Common.c`다.

## 1. SDK 구조와 의존성

### 저장소와 빌드 결과물

| 경로 | 내용 |
|---|---|
| `src/include/com/amazonaws/kinesis/video/webrtcclient/Include.h` | 공개 API 전체. README도 "All Public APIs are documented in our Include.h"라고 적는다 |
| `src/source/` | `PeerConnection`, `Ice`, `Stun`, `Sdp`, `Rtp`, `Rtcp`, `Srtp`, `Sctp`, `Crypto`, `Signaling`, `Metrics`, `Threadpool` |
| `samples/common/` | `Common.c`(시그널링·세션 관리 공통 로직), `GstMedia.c`(GStreamer 송출), `StaticMedia.c`(파일 프레임 송출) |
| `samples/p2p/` | `kvsWebRTCClientMaster.c`, `kvsWebRTCClientMasterGstSample.c`, `kvsWebRTCClientViewer.c` 등 |
| `samples/webrtcstorage/` | WebRTC 인제스트([21장](/study/webrtc/21-kvs-ingestion-storage)) 샘플 |
| `certs/cert.pem` | 기본 CA 번들(`AWS_KVS_CACERT_PATH`로 바꿀 수 있다) |

빌드하면 라이브러리가 두 개 나온다. `kvsWebrtcClient`는 PeerConnection·ICE·DTLS/SRTP·SCTP·RTP 같은 WebRTC 스택이고, `kvsWebrtcSignalingClient`는 KVS 시그널링 전용 클라이언트다. 시그널링 클라이언트는 다시 두 AWS 라이브러리에 기댄다. producer-c 저장소의 `kvsCommonLws`가 자격증명 provider·SigV4 서명·libwebsockets 기반 HTTPS/WSS를 맡고, PIC(Platform Independent Code)의 `kvspic`이 스레드·타이머·로깅·자료구조를 맡는다. 둘 다 CMake가 함께 내려받아 빌드하며, `PRODUCER_C_VERSION_OVERRIDE`·`PIC_VERSION_OVERRIDE`로 git 태그를 고정할 수 있다.

![KVS C SDK 계층 구조. 맨 위 애플리케이션 계층(samples 또는 직접 작성한 앱) 아래에 Include.h 공개 API로 노출되는 kvsWebrtcClient(PeerConnection·ICE·DTLS/SRTP·SCTP·RTP)와 kvsWebrtcSignalingClient(시그널링 상태 머신·WSS·캐시)가 있고, 시그널링 클라이언트는 자격증명·서명을 위해 producer-c의 kvsCommonLws를 쓴다. 그 아래 kvspic과 서드파티 OpenSSL/mbedTLS·libsrtp2·usrsctp·libwebsockets·jsmn이 있다](/images/study-webrtc/19-sdk-layers-light.png)
![KVS C SDK 계층 구조. 맨 위 애플리케이션 계층(samples 또는 직접 작성한 앱) 아래에 Include.h 공개 API로 노출되는 kvsWebrtcClient(PeerConnection·ICE·DTLS/SRTP·SCTP·RTP)와 kvsWebrtcSignalingClient(시그널링 상태 머신·WSS·캐시)가 있고, 시그널링 클라이언트는 자격증명·서명을 위해 producer-c의 kvsCommonLws를 쓴다. 그 아래 kvspic과 서드파티 OpenSSL/mbedTLS·libsrtp2·usrsctp·libwebsockets·jsmn이 있다](/images/study-webrtc/19-sdk-layers-dark.png)

### 서드파티 의존성

기본값(`-DBUILD_DEPENDENCIES=ON`)이면 CMake가 아래 라이브러리를 GitHub에서 받아 소스 빌드하므로 미리 설치할 것이 거의 없다. 배포판 패키지에 링크하려면 README가 요구하는 버전을 맞춰야 한다.

| 라이브러리 | 역할 | 시스템 라이브러리에 링크할 때 요구 버전 |
|---|---|---|
| OpenSSL 또는 mbedTLS | DTLS·TLS·암호 연산 | OpenSSL `= 1.1.1x` 또는 `>= 3.0.0` / mbedTLS `>= 2.25.0`(기본 3.6.x) |
| libsrtp2 | SRTP 암복호화 | `<= 2.5.0` |
| usrsctp | DataChannel용 SCTP | `<= 0.9.5.0` |
| libwebsockets | 시그널링 WSS·HTTPS | `>= 4.2.0` |
| jsmn | JSON 파싱 | (README 의존성 목록에만 있다) |

README의 Key Features는 VP8·H.264·Opus·G.711(A-law/µ-law), DataChannel, NACK, STUN/TURN, IPv4/IPv6, 시그널링 클라이언트 내장, Storage for WebRTC를 꼽는다. 샘플 인자로는 H.265도 받는다(`Allowed video-codec: h264 (default), h265`). README는 라이브러리 크기를 "Sub 200k"라고 적는다.

이 SDK의 성격을 한 줄로 요약하면 "인코딩된 프레임을 받아 패킷화·암호화·전송만 하는 스택"이다. README도 "Developer Controlled Media Pipeline — Raw Media for Input/Output"이라고 적는다. libwebrtc처럼 캡처·인코더·혼잡 제어 루프를 다 가진 엔진이 아니라서, 카메라 캡처와 인코딩은 앱이 하고 SDK에는 H.264 access unit을 넘긴다. 디바이스 입장에서는 하드웨어 인코더를 그대로 붙일 수 있다는 장점이 있다. 대신 대역폭 추정 결과를 콜백으로 받아 인코더 비트레이트를 앱이 직접 바꿔야 한다(3절).

### 빌드

```bash
git clone https://github.com/awslabs/amazon-kinesis-video-streams-webrtc-sdk-c.git \
  --single-branch -b main kvs-webrtc-sdk

# Ubuntu / Raspberry Pi OS: GStreamer 샘플까지 빌드하려면
sudo apt-get install cmake m4 pkg-config libssl-dev libcurl4-openssl-dev liblog4cplus-dev \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-plugins-base-apps \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools

mkdir -p kvs-webrtc-sdk/build && cd kvs-webrtc-sdk/build
cmake .. -DBUILD_DEPENDENCIES=ON -DUSE_OPENSSL=ON -DUSE_OPENSSL3=ON -DPARALLEL_BUILD=ON
make -j
```

::: warning CMake 3.x만 지원한다
README는 "requires 3.x, CMake 4.x is not yet supported"라고 적는다. 최신 Homebrew나 pip로 깐 CMake가 4.x라면 3.x를 따로 설치해야 한다. GStreamer 샘플은 `pkg-config`가 GStreamer를 찾을 때만 빌드된다.
:::

자주 만지는 CMake 옵션은 다음과 같다.

| 옵션 | 기본 | 의미 |
|---|---|---|
| `-DBUILD_SAMPLE` | ON | 샘플 실행 파일 빌드. 제품 빌드에서는 끈다 |
| `-DIOT_CORE_ENABLE_CREDENTIALS` | OFF | 샘플이 IoT 인증서 자격증명을 쓰도록 빌드(4절) |
| `-DENABLE_DATA_CHANNEL` | ON | DataChannel 포함 |
| `-DBUILD_DEPENDENCIES` | ON | 의존 라이브러리를 소스에서 빌드. `BUILD_WEBSOCKETS`·`BUILD_SRTP`·`BUILD_USRSCTP`로 개별 지정 가능 |
| `-DUSE_OPENSSL` / `-DUSE_MBEDTLS` | OpenSSL | 암호 백엔드 선택 |
| `-DUSE_OPENSSL3` | OFF | OpenSSL 3.x(태그 `openssl-3.5.7`)로 빌드. v1.20.0부터 지원, 시스템 OpenSSL이 3.0 이상이면 자동 ON |
| `-DBUILD_STATIC_LIBS` | OFF | SDK와 서드파티를 모두 정적 라이브러리로 |
| `-DMAX_SDP_SESSION_MEDIA_COUNT` | 5 | SDP m= 섹션 최대 수. 슬롯 하나당 스택의 `SessionDescription` 구조체가 약 140 KB 커진다 |
| `-DENABLE_KVS_THREADPOOL` | OFF | 연결 수립 지연을 줄이는 스레드풀 |
| `-DKVS_STACK_SIZE` | 시스템 기본 | `THREAD_CREATE()`로 만드는 스레드의 스택 크기 |
| `-DLINK_PROFILER` | OFF | gperftools 링크(힙·CPU 프로파일) |
| `-DPARALLEL_BUILD` | OFF | 의존성을 여러 코어로 빌드 |

<strong>OpenSSL과 mbedTLS 중 무엇을 고를까.</strong> SDK는 아직 기본값으로 OpenSSL 1.1.1t를 빌드하는데, OpenSSL 1.1.1은 2023년 9월에 지원이 끝났다. README도 새 배포에는 3.x를 권한다. 메모리가 빠듯한 보드라면 mbedTLS가 후보다. 이때 주의할 점은 배포판의 libwebsockets·libsrtp 패키지가 보통 OpenSSL로 빌드돼 있다는 것이다. mbedTLS를 쓰면서 시스템 패키지에 링크하면 링크 오류나 런타임 오류가 날 수 있으니 `-DBUILD_DEPENDENCIES=ON`으로 같이 소스 빌드하는 편이 안전하다. mbedTLS 경로는 엔트로피를 `/dev/urandom`에서 얻는데, README는 이게 약한 시스템이면 `MBEDTLS_ENTROPY_HARDWARE_ALT`로 하드웨어 엔트로피 소스를 연결하라고 "strongly suggested"로 권한다.

## 2. kvsWebrtcClientMaster 샘플 흐름

먼저 샘플을 돌려 본다. 빌드 디렉터리에서 채널 이름을 넘기면 된다. 채널이 없으면 샘플이 만든다.

```bash
cd kvs-webrtc-sdk/build
export AWS_ACCESS_KEY_ID=...            # 개발용. 제품에서는 4절의 IoT 자격증명
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=ap-northeast-2  # 미설정 시 us-west-2
export AWS_KVS_LOG_LEVEL=3                # INFO

# <channelName> <mediaType> <audio-codec> <video-codec>
./samples/kvsWebrtcClientMaster tractor-0017 audio-video opus h264
```

`mediaType`은 `audio-video`(기본)와 `video-only`, 비디오 코덱은 `h264`(기본)와 `h265`를 받는다. 이 샘플은 카메라 대신 `h264SampleFrames/frame-0001.h264`부터 1,500장, `opusSampleFrames`의 오디오 프레임을 반복 송출한다. "Signaling client connection to socket established" 로그가 보이면 KVS 콘솔의 미디어 재생 뷰어나 JS SDK 테스트 페이지에서 같은 채널로 viewer를 붙여 확인한다.

![kvsWebrtcClientMaster 흐름 시퀀스. 디바이스는 ① 자격증명 provider를 만들고 ② createSignalingClientSync·signalingClientFetchSync로 KVS API에 Describe(필요 시 Create)·GetEndpoint·GetIceServerConfig를 호출한 뒤 ③ signalingClientConnectSync로 ConnectAsMaster WSS 연결을 연다. 브라우저가 ConnectAsViewer 후 보낸 SDP_OFFER가 ④ messageReceivedFn으로 들어오면 ⑤ createPeerConnection·addTransceiver·setRemoteDescription·createAnswer를 하고 ⑥ SDP_ANSWER를 보낸다. ⑦ ICE_CANDIDATE를 교환한 뒤 ⑧ ICE·DTLS가 끝나면 writeFrame으로 SRTP 미디어가 P2P 또는 TURN으로 흐른다](/images/study-webrtc/19-master-flow-light.png)
![kvsWebrtcClientMaster 흐름 시퀀스. 디바이스는 ① 자격증명 provider를 만들고 ② createSignalingClientSync·signalingClientFetchSync로 KVS API에 Describe(필요 시 Create)·GetEndpoint·GetIceServerConfig를 호출한 뒤 ③ signalingClientConnectSync로 ConnectAsMaster WSS 연결을 연다. 브라우저가 ConnectAsViewer 후 보낸 SDP_OFFER가 ④ messageReceivedFn으로 들어오면 ⑤ createPeerConnection·addTransceiver·setRemoteDescription·createAnswer를 하고 ⑥ SDP_ANSWER를 보낸다. ⑦ ICE_CANDIDATE를 교환한 뒤 ⑧ ICE·DTLS가 끝나면 writeFrame으로 SRTP 미디어가 P2P 또는 TURN으로 흐른다](/images/study-webrtc/19-master-flow-dark.png)

### 시그널링 클라이언트의 상태 머신

`createSignalingClientSync`로 만든 클라이언트는 `Include.h`의 `SIGNALING_CLIENT_STATE` 순서대로 움직인다. 각 상태가 18장의 API 하나에 대응한다.

| 상태 | 하는 일 |
|---|---|
| `NEW` → `GET_CREDENTIALS` | 자격증명 provider에서 토큰을 받는다 |
| `DESCRIBE` | `DescribeSignalingChannel`로 채널 정보 조회 |
| `CREATE` | 채널이 없으면 `CreateSignalingChannel` |
| `GET_ENDPOINT` | `GetSignalingChannelEndpoint`로 WSS·HTTPS 엔드포인트 조회 |
| `GET_ICE_CONFIG` | `GetIceServerConfig`로 TURN 서버·임시 credential 조회 |
| `READY` | 연결 준비 완료(`signalingClientFetchSync`가 여기까지 진행) |
| `CONNECTING` → `CONNECTED` | `ConnectAsMaster` WSS 연결(`signalingClientConnectSync`) |
| `DISCONNECTED` | 연결이 끊김. `reconnect` 플래그가 켜져 있으면 다시 시도 |

인제스트 모드 채널이면 `DESCRIBE_MEDIA`, `JOIN_SESSION` 계열 상태가 더 끼어든다(21장).

### 핵심 API 호출 골격

아래는 샘플의 `Common.c`·`kvsWebRTCClientMaster.c`에서 핵심 호출만 남겨 재구성한 골격이다. 함수 이름과 구조체 필드는 v1.20.0 `Include.h` 기준이다. 오류 처리는 SDK 관례대로 `CHK_STATUS` 매크로(실패 시 `CleanUp` 라벨로 점프)를 쓴다.

```c
#include <com/amazonaws/kinesis/video/webrtcclient/Include.h>

typedef struct {
    CHAR peerId[MAX_SIGNALING_CLIENT_ID_LEN + 1];   // viewer의 ClientId
    PRtcPeerConnection pc;
    PRtcRtpTransceiver videoTx;
} ViewerSession, *PViewerSession;

static SIGNALING_CLIENT_HANDLE gSignaling = INVALID_SIGNALING_CLIENT_HANDLE_VALUE;
static PAwsCredentialProvider gCreds = NULL;
static PCHAR gRegion = "ap-northeast-2";

/* 1~3) 자격증명 → 시그널링 클라이언트 생성 → fetch → connect */
STATUS startMaster(PCHAR channelName)
{
    STATUS retStatus = STATUS_SUCCESS;
    ChannelInfo channelInfo;
    SignalingClientInfo clientInfo;
    SignalingClientCallbacks callbacks;

    CHK_STATUS(initKvsWebRtc());                     // 프로세스당 한 번

    // IoT 인증서로 임시 자격증명을 받는 provider (4절). 개발 중엔 createStaticCredentialProvider
    CHK_STATUS(createLwsIotCredentialProvider(
        getenv("AWS_IOT_CORE_CREDENTIAL_ENDPOINT"), getenv("AWS_IOT_CORE_CERT"),
        getenv("AWS_IOT_CORE_PRIVATE_KEY"), "/etc/kvs/cert.pem",
        getenv("AWS_IOT_CORE_ROLE_ALIAS"), channelName /* thing 이름 = 채널 이름 */, &gCreds));

    MEMSET(&channelInfo, 0, SIZEOF(channelInfo));
    channelInfo.version = CHANNEL_INFO_CURRENT_VERSION;
    channelInfo.pChannelName = channelName;
    channelInfo.pRegion = gRegion;
    channelInfo.channelType = SIGNALING_CHANNEL_TYPE_SINGLE_MASTER;
    channelInfo.channelRoleType = SIGNALING_CHANNEL_ROLE_TYPE_MASTER;
    channelInfo.cachingPolicy = SIGNALING_API_CALL_CACHE_TYPE_FILE;   // Describe·GetEndpoint 결과를 파일에 캐시
    channelInfo.cachingPeriod = SIGNALING_API_CALL_CACHE_TTL_SENTINEL_VALUE;
    channelInfo.retry = TRUE;                        // 네트워크 호출 재시도
    channelInfo.reconnect = TRUE;                    // 연결이 끊기면 재연결 시도
    channelInfo.messageTtl = 0;                      // 0 = 기본 60초
    channelInfo.pCertPath = "/etc/kvs/cert.pem";

    MEMSET(&clientInfo, 0, SIZEOF(clientInfo));
    clientInfo.version = SIGNALING_CLIENT_INFO_CURRENT_VERSION;
    clientInfo.loggingLevel = LOG_LEVEL_WARN;
    STRCPY(clientInfo.clientId, "ProducerMaster");   // 샘플의 SAMPLE_MASTER_CLIENT_ID

    MEMSET(&callbacks, 0, SIZEOF(callbacks));
    callbacks.version = SIGNALING_CLIENT_CALLBACKS_CURRENT_VERSION;
    callbacks.messageReceivedFn = onSignalingMessage;   // SDP_OFFER, ICE_CANDIDATE 수신
    callbacks.errorReportFn = onSignalingError;
    callbacks.stateChangeFn = onSignalingState;

    CHK_STATUS(createSignalingClientSync(&clientInfo, &channelInfo, &callbacks, gCreds, &gSignaling));
    CHK_STATUS(signalingClientFetchSync(gSignaling));    // Describe(→Create)·GetEndpoint·GetIceServerConfig
    CHK_STATUS(signalingClientConnectSync(gSignaling));  // ConnectAsMaster

CleanUp:
    return retStatus;
}

/* 5) viewer마다 PeerConnection 하나 */
STATUS createViewerSession(PCHAR peerId, PViewerSession s)
{
    STATUS retStatus = STATUS_SUCCESS;
    RtcConfiguration cfg;
    RtcMediaStreamTrack video;
    RtcRtpTransceiverInit init;
    PIceConfigInfo pIce;
    UINT32 iceCount, j, k = 1;

    STRNCPY(s->peerId, peerId, MAX_SIGNALING_CLIENT_ID_LEN);
    MEMSET(&cfg, 0, SIZEOF(cfg));
    SNPRINTF(cfg.iceServers[0].urls, MAX_ICE_CONFIG_URI_LEN, KINESIS_VIDEO_STUN_URL,
             gRegion, KINESIS_VIDEO_STUN_URL_POSTFIX);   // stun:stun.kinesisvideo.<region>.amazonaws.com:443

    // TURN: fetch 단계에서 받아 둔 GetIceServerConfig 결과(credential TTL 300초)
    CHK_STATUS(signalingClientGetIceConfigInfoCount(gSignaling, &iceCount));
    if (iceCount > 0) {
        CHK_STATUS(signalingClientGetIceConfigInfo(gSignaling, 0, &pIce));  // 샘플도 수집 시간을 줄이려고 하나만 쓴다
        for (j = 0; j < pIce->uriCount; j++, k++) {
            STRNCPY(cfg.iceServers[k].urls, pIce->uris[j], MAX_ICE_CONFIG_URI_LEN);
            STRNCPY(cfg.iceServers[k].username, pIce->userName, MAX_ICE_CONFIG_USER_NAME_LEN);
            STRNCPY(cfg.iceServers[k].credential, pIce->password, MAX_ICE_CONFIG_CREDENTIAL_LEN);
        }
    }

    CHK_STATUS(createPeerConnection(&cfg, &s->pc));
    CHK_STATUS(peerConnectionOnIceCandidate(s->pc, (UINT64) s, onLocalCandidate));
    CHK_STATUS(peerConnectionOnConnectionStateChange(s->pc, (UINT64) s, onPcStateChange));
    CHK_STATUS(addSupportedCodec(s->pc, RTC_CODEC_H264_PROFILE_42E01F_LEVEL_ASYMMETRY_ALLOWED_PACKETIZATION_MODE));

    MEMSET(&video, 0, SIZEOF(video));
    video.kind = MEDIA_STREAM_TRACK_KIND_VIDEO;
    video.codec = RTC_CODEC_H264_PROFILE_42E01F_LEVEL_ASYMMETRY_ALLOWED_PACKETIZATION_MODE;
    STRCPY(video.streamId, "tractor-0017");
    STRCPY(video.trackId, "front-cam");
    MEMSET(&init, 0, SIZEOF(init));
    init.direction = RTC_RTP_TRANSCEIVER_DIRECTION_SENDONLY;   // 샘플은 SENDRECV
    CHK_STATUS(addTransceiver(s->pc, &video, &init, &s->videoTx));

CleanUp:
    return retStatus;
}

/* 4~6) 오퍼 처리 → 앤서 전송 */
STATUS answerOffer(PViewerSession s, PSignalingMessage pOffer)
{
    STATUS retStatus = STATUS_SUCCESS;
    RtcSessionDescriptionInit offer, answer;
    SignalingMessage msg;
    UINT32 len = MAX_SIGNALING_MESSAGE_LEN;

    MEMSET(&offer, 0, SIZEOF(offer));
    MEMSET(&answer, 0, SIZEOF(answer));
    MEMSET(&msg, 0, SIZEOF(msg));

    CHK_STATUS(deserializeSessionDescriptionInit(pOffer->payload, pOffer->payloadLen, &offer));
    CHK_STATUS(setRemoteDescription(s->pc, &offer));
    CHK_STATUS(setLocalDescription(s->pc, &answer));  // 샘플 순서: 빈 init으로 먼저 호출해 ICE 수집 시작
    CHK_STATUS(createAnswer(s->pc, &answer));          // 원격이 Trickle ICE를 지원할 때만 바로 앤서

    CHK_STATUS(serializeSessionDescriptionInit(&answer, msg.payload, &len));
    msg.version = SIGNALING_MESSAGE_CURRENT_VERSION;
    msg.messageType = SIGNALING_MESSAGE_TYPE_ANSWER;
    STRNCPY(msg.peerClientId, s->peerId, MAX_SIGNALING_CLIENT_ID_LEN);   // master는 수신자 지정이 필수
    msg.payloadLen = (UINT32) STRLEN(msg.payload);
    CHK_STATUS(signalingClientSendMessageSync(gSignaling, &msg));

CleanUp:
    return retStatus;
}

/* 로컬 후보 → ICE_CANDIDATE 메시지 (candidateJson == NULL이면 수집 완료) */
VOID onLocalCandidate(UINT64 customData, PCHAR candidateJson)
{
    PViewerSession s = (PViewerSession) customData;
    SignalingMessage msg;
    if (candidateJson == NULL) return;
    MEMSET(&msg, 0, SIZEOF(msg));
    msg.version = SIGNALING_MESSAGE_CURRENT_VERSION;
    msg.messageType = SIGNALING_MESSAGE_TYPE_ICE_CANDIDATE;
    STRNCPY(msg.peerClientId, s->peerId, MAX_SIGNALING_CLIENT_ID_LEN);
    msg.payloadLen = (UINT32) STRNLEN(candidateJson, MAX_SIGNALING_MESSAGE_LEN);
    STRNCPY(msg.payload, candidateJson, msg.payloadLen);
    signalingClientSendMessageSync(gSignaling, &msg);   // 실제 샘플은 전송 뮤텍스로 직렬화한다
}

/* 시그널링 수신 콜백 */
STATUS onSignalingMessage(UINT64 customData, PReceivedSignalingMessage pRecv)
{
    STATUS retStatus = STATUS_SUCCESS;
    PSignalingMessage m = &pRecv->signalingMessage;
    PViewerSession s = findSession(m->peerClientId);    // ClientId 해시 → 세션

    switch (m->messageType) {
        case SIGNALING_MESSAGE_TYPE_OFFER:
            CHK_STATUS(allocSession(&s));
            CHK_STATUS(createViewerSession(m->peerClientId, s));
            CHK_STATUS(answerOffer(s, m));
            break;
        case SIGNALING_MESSAGE_TYPE_ICE_CANDIDATE:
            if (s != NULL) {                              // 샘플은 오퍼보다 먼저 온 후보를 큐에 보관한다
                RtcIceCandidateInit cand;
                CHK_STATUS(deserializeRtcIceCandidateInit(m->payload, m->payloadLen, &cand));
                CHK_STATUS(addIceCandidate(s->pc, cand.candidate));
            }
            break;
        default:
            break;
    }
CleanUp:
    return retStatus;
}
```

연결이 끝나면 미디어 스레드가 프레임마다 모든 세션에 `writeFrame`을 호출한다. 이 부분은 3절의 GStreamer 콜백에서 같이 본다. 종료할 때는 `closePeerConnection` → `freePeerConnection` → `freeSignalingClient` → `freeIotCredentialProvider` → `deinitKvsWebRtc` 순서로 정리한다.

### 샘플 코드에서 읽어 둘 동작

<strong>API 순서가 브라우저와 다르다.</strong> 브라우저는 `createAnswer` → `setLocalDescription` 순서지만, 샘플의 `handleOffer`는 빈 `RtcSessionDescriptionInit`으로 `setLocalDescription`을 먼저 불러 ICE 수집을 시작하고 그다음 `createAnswer`로 SDP를 채운다. 원격이 Trickle ICE를 지원하지 않으면(`canTrickleIceCandidates`가 FALSE) 앤서를 바로 보내지 않고, `onIceCandidate`에 NULL이 와서 수집이 끝났을 때 보낸다. 브라우저 viewer는 Trickle ICE를 쓰므로 보통은 바로 보낸다.

<strong>viewer마다 PeerConnection이 하나씩 생긴다.</strong> 샘플은 viewer의 ClientId를 CRC32 해시해 세션을 찾는 해시 테이블과 세션 배열을 둔다. 배열 크기 `DEFAULT_MAX_CONCURRENT_STREAMING_SESSION`은 10으로, KVS 채널의 기본 viewer 한도 10과 같다. 한도를 넘으면 "Max simultaneous streaming session count reached." 로그를 남기고 오퍼를 버린다. viewer 한도(`ConnectAsViewer connections per signaling channel`)는 Service Quotas에서 올릴 수 있지만, 그때는 디바이스 쪽 배열도 같이 키워야 한다. 같은 ClientId로 오퍼가 다시 오면 기존 세션이 살아 있을 때는 같은 PeerConnection으로 재협상하고, 이미 끊긴 세션이면 버리고 새로 만든다.

<strong>업링크가 viewer 수만큼 곱해진다.</strong> [16장](/study/webrtc/16-aws-landscape)에서 강조했듯 KVS 기본 모드는 SFU가 아니다. 운영자 4명이 같은 트랙터를 보면 디바이스는 같은 프레임을 4번 패킷화·SRTP 암호화해 4개 경로로 보낸다. 1.5 Mbps 스트림이면 LTE 업링크로 6 Mbps가 필요하다. 업링크 예산이 작은 농기계라면 동시 viewer 상한을 제품 정책으로 정하거나(백엔드에서 viewer 세션 발급을 제한, [20장](/study/webrtc/20-kvs-viewer-backend)) 21장의 인제스트 모드를 검토한다.

<strong>시그널링 연결은 오래 유지되지 않는다.</strong> KVS는 `ConnectAsMaster` 연결을 최대 1시간(3,600초), idle 10분(600초)으로 제한하고, `GO_AWAY` 뒤 유예는 60초다. 셋 다 조정할 수 없는 hard 한도다. `channelInfo.reconnect = TRUE`면 SDK가 끊긴 연결을 다시 맺으려 시도하고, 샘플은 여기에 더해 5초마다 깨는 감시 루프(`sessionCleanupWait`)를 돈다. 이 루프는 `STATUS_SIGNALING_ICE_CONFIG_REFRESH_FAILED`나 `STATUS_SIGNALING_RECONNECT_FAILED` 오류가 오면 시그널링 클라이언트를 새로 만들고, 상태가 `READY`에 머물러 있으면 `signalingClientConnectSync`를 다시 부른다. 24시간 켜져 있는 농기계라면 이 감시 루프를 그대로 가져가야 한다. 참고로 `GetIceServerConfig`의 `SessionExpiredException` 설명에는 "session is valid for 45 minutes"라는 별도 수치가 있어 1시간 한도와 숫자가 다르다. 둘의 관계는 문서에 설명이 없으니 재연결 로직은 어느 쪽이든 견디게 짠다.

<strong>캐시가 재부팅 폭주를 막는다.</strong> 샘플은 `cachingPolicy = SIGNALING_API_CALL_CACHE_TYPE_FILE_EXCEPT_DESCRIBE_MEDIA`를 쓴다. `DescribeSignalingChannel`·`GetSignalingChannelEndpoint` 결과를 파일에 남겨 재시작해도 다시 부르지 않는다. 이 두 API는 채널당 5 TPS 한도라서, 전원이 불안정해 재부팅을 반복하는 디바이스가 있으면 캐시가 없을 때 스로틀(`ClientLimitExceededException`)에 걸리기 쉽다.

<strong>DTLS 인증서 생성이 느리다.</strong> README에 따르면 저사양 임베디드에서 `createCertificateAndKey`가 5~15초 걸릴 수 있고, 오퍼를 받을 때마다 호출된다. 샘플은 타이머로 인증서를 미리 만들어 큐에 쌓아 두고(`KVS_PRE_GENERATE_CERT_ENABLED` 기본 TRUE, 주기 3초, 최대 2개) PeerConnection을 만들 때 하나씩 꺼내 쓴다. README는 인증서를 연결마다 바꾸라고 권한다([10장](/study/webrtc/10-dtls-srtp)의 `a=fingerprint` 검증과 연결된다).

### viewer 샘플은 언제 쓰나

`kvsWebrtcClientViewer <channelName> <audio-codec> <video-codec>`는 같은 SDK로 viewer 역할을 한다. ClientId를 `ConsumerViewer_<난수>`로 만들고, 세션을 만든 뒤 `setLocalDescription` → `createOffer` → `signalingClientSendMessageSync`(OFFER)로 오퍼를 보낸다. 받은 프레임은 `transceiverOnFrame` 콜백으로 들어오며 샘플은 크기만 로그로 찍는다. `kvsWebrtcClientViewerGstSample`은 받은 미디어를 `filesink`로 저장하는데, README는 `matroskamux`가 중간에 캡스가 바뀌면 처리하지 못하는 문제를 Known issue로 적는다.

현장에서는 쓸모가 꽤 있다. 브라우저 없이 master를 검증하는 CI 통합 테스트, 농장 사무실 엣지 게이트웨이가 여러 농기계 영상을 받아 로컬 녹화하는 구성, 디바이스 간 영상 전달이 그런 경우다.

## 3. GStreamer 샘플과 하드웨어 인코더 연동

`kvsWebrtcClientMasterGstSample`은 송출 소스를 GStreamer 파이프라인으로 바꾼 샘플이다.

```bash
# <channelName> <mediaType> <sourceType>
./samples/kvsWebrtcClientMasterGstSample tractor-0017 video-only devicesrc
./samples/kvsWebrtcClientMasterGstSample tractor-0017 audio-video testsrc opus h264
./samples/kvsWebrtcClientMasterGstSample tractor-0017 video-only rtspsrc rtsp://192.168.0.64/stream1
```

`sourceType`은 `testsrc`(videotestsrc), `devicesrc`(`autovideosrc`·`autoaudiosrc`, 기본), `rtspsrc`(IP 카메라) 중 하나다. viewer가 보낸 오디오는 `autoaudiosink`로 재생한다.

### appsink → writeFrame 구조

샘플의 `GstMedia.c`가 하는 일은 단순하다. 파이프라인 끝을 `appsink name=appsink-video emit-signals=TRUE`로 두고, `"new-sample"` 시그널에 콜백을 건다. 콜백은 버퍼를 꺼내 `Frame` 구조체에 담고, 연결된 모든 세션에 `writeFrame`을 호출한다.

![GStreamer appsink에서 writeFrame으로 이어지는 구조. 위쪽 GStreamer 파이프라인은 v4l2src(카메라) → v4l2convert → HW 인코더(v4l2h264enc 등) → h264parse config-interval=-1 → appsink 순서이고 caps는 byte-stream·alignment=au·profile=baseline이다. appsink의 new-sample 시그널이 on_new_sample() 콜백을 부르고, 콜백은 세션 1·2·…·N(각각 PeerConnection)에 writeFrame을 N번 호출해 패킷화·SRTP 암호화·송신한다. 각 세션의 TWCC 추정은 점선으로 하나뿐인 인코더의 bitrate로 되돌아가 N개 세션이 인코더 하나를 공유한다](/images/study-webrtc/19-gst-appsink-light.png)
![GStreamer appsink에서 writeFrame으로 이어지는 구조. 위쪽 GStreamer 파이프라인은 v4l2src(카메라) → v4l2convert → HW 인코더(v4l2h264enc 등) → h264parse config-interval=-1 → appsink 순서이고 caps는 byte-stream·alignment=au·profile=baseline이다. appsink의 new-sample 시그널이 on_new_sample() 콜백을 부르고, 콜백은 세션 1·2·…·N(각각 PeerConnection)에 writeFrame을 N번 호출해 패킷화·SRTP 암호화·송신한다. 각 세션의 TWCC 추정은 점선으로 하나뿐인 인코더의 bitrate로 되돌아가 N개 세션이 인코더 하나를 공유한다](/images/study-webrtc/19-gst-appsink-dark.png)

샘플 콜백을 실제 카메라에 맞게 다듬으면 다음과 같다.

```c
#include <gst/gst.h>
#include <gst/app/gstappsink.h>

static ViewerSession* gSessions[10];
static UINT32 gSessionCount = 0;
static MUTEX gSessionsLock;

static VOID sendVideoFrame(PBYTE data, UINT32 size, UINT64 pts100ns, BOOL key)
{
    Frame f;
    UINT32 i;
    MEMSET(&f, 0, SIZEOF(f));
    f.version = FRAME_CURRENT_VERSION;
    f.trackId = DEFAULT_VIDEO_TRACK_ID;
    f.frameData = data;
    f.size = size;
    f.presentationTs = f.decodingTs = pts100ns;          // SDK 시간 단위는 100 ns
    f.flags = key ? FRAME_FLAG_KEY_FRAME : FRAME_FLAG_NONE;

    MUTEX_LOCK(gSessionsLock);
    for (i = 0; i < gSessionCount; i++) {
        STATUS st = writeFrame(gSessions[i]->videoTx, &f);   // 세션마다 패킷화 + SRTP
        if (st == STATUS_SRTP_NOT_READY_YET) {
            // DTLS가 아직 안 끝났다. 버리고, 이 세션이 준비되면 키프레임부터 보내야 한다
        }
    }
    MUTEX_UNLOCK(gSessionsLock);
}

static GstFlowReturn onNewVideoSample(GstElement* sink, gpointer user)
{
    GstSample* sample = gst_app_sink_pull_sample(GST_APP_SINK(sink));
    GstBuffer* buf = gst_sample_get_buffer(sample);
    GstMapInfo map;

    if (GST_BUFFER_PTS_IS_VALID(buf) && gst_buffer_map(buf, &map, GST_MAP_READ)) {
        GstSegment* seg = gst_sample_get_segment(sample);
        GstClockTime rt = gst_segment_to_running_time(seg, GST_FORMAT_TIME, GST_BUFFER_PTS(buf));
        BOOL key = !GST_BUFFER_FLAG_IS_SET(buf, GST_BUFFER_FLAG_DELTA_UNIT);
        sendVideoFrame(map.data, (UINT32) map.size, rt / 100 /* ns → 100 ns */, key);
        gst_buffer_unmap(buf, &map);
    }
    gst_sample_unref(sample);
    return GST_FLOW_OK;
}

/* 파이프라인 연결 */
// GstElement* appsink = gst_bin_get_by_name(GST_BIN(pipeline), "appsink-video");
// g_signal_connect(appsink, "new-sample", G_CALLBACK(onNewVideoSample), NULL);
// gst_element_set_state(pipeline, GST_STATE_PLAYING);
```

`appsink` 앞 캡스는 세 가지를 맞춘다. `stream-format=byte-stream`은 Annex-B 시작 코드가 붙은 형식이다. SDK가 이 시작 코드로 NAL 단위를 잘라 RTP로 패킷화한다([08장](/study/webrtc/08-rtp-codecs)의 FU-A). `alignment=au`는 버퍼 하나가 access unit(프레임) 하나라는 뜻이다. `profile=baseline`은 SDK가 SDP에 광고하는 `RTC_CODEC_H264_PROFILE_42E01F_LEVEL_ASYMMETRY_ALLOWED_PACKETIZATION_MODE`(profile-level-id `42e01f`, Constrained Baseline)와 맞추기 위해서다. B-프레임은 끈다. 샘플의 x264enc 설정도 `bframes=0 tune=zerolatency`다. `h264parse config-interval=-1`은 키프레임마다 SPS/PPS를 다시 넣어, 중간에 붙은 viewer도 첫 키프레임부터 디코딩할 수 있게 한다. README는 H.265에서는 이 설정이 없으면 첫 키프레임 뒤에 화면이 멈춘다고 적는다.

### 하드웨어 인코더 파이프라인

샘플 소스(`GstMedia.c`)의 주석에 Raspberry Pi 하드웨어 인코더 예시가 들어 있다.

```text
v4l2src device=/dev/video0 ! queue ! v4l2convert !
video/x-raw,format=I420,width=640,height=480,framerate=30/1 !
v4l2h264enc ! h264parse !
video/x-h264,stream-format=byte-stream,alignment=au,width=640,height=480,framerate=30/1,profile=baseline,level=(string)4 !
appsink sync=TRUE emit-signals=TRUE name=appsink-video
```

Jetson 계열은 NVENC를 쓰는 `nvv4l2h264enc`로 바꾼다. 아래 속성 이름은 JetPack 버전마다 다를 수 있으니 보드에서 `gst-inspect-1.0 nvv4l2h264enc`로 확인한다.

```text
nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=30/1 !
nvv4l2h264enc name=sampleVideoEncoder insert-sps-pps=true idrinterval=30 bitrate=2000000 !
h264parse config-interval=-1 !
video/x-h264,stream-format=byte-stream,alignment=au !
appsink sync=TRUE emit-signals=TRUE name=appsink-video
```

Raspberry Pi 5에는 이전 세대에 있던 H.264 하드웨어 인코더가 없어서 소프트웨어 인코딩(x264enc)으로 돌아가야 한다. Raspberry Pi도 Pi 5의 H.264 인코딩은 CPU 인코딩 성능 문서로 안내한다. 보드를 고를 때 미리 확인한다. 하드웨어 인코더 일반론은 [13장](/study/webrtc/13-native-webrtc)에서 다뤘다.

### 실전에서 걸리는 지점

1. <strong>타임스탬프.</strong> 샘플 콜백은 버퍼 PTS를 계산만 하고 쓰지 않는다. 대신 세션마다 `SAMPLE_VIDEO_FRAME_DURATION`(25 fps 가정)씩 타임스탬프를 늘린다. 실제 카메라는 프레임 간격이 흔들리고 조도에 따라 fps가 바뀌기도 하므로, 위 코드처럼 running time(ns)을 100 ns 단위로 바꿔 넣는 편이 수신 측 지터 버퍼와 립싱크에 맞다.
2. <strong>인코더 하나를 N 세션이 공유한다.</strong> 샘플은 TWCC 피드백(`sampleOnPeerCongestionFeedback`)으로 세션별 목표 비트레이트를 계산하고(비디오 384~2,500 kbps 범위), 이름이 `sampleVideoEncoder`인 인코더의 `bitrate` 속성을 바꾼다. 그런데 인코더는 하나라서 마지막에 쓴 세션의 값이 이긴다. LTE로 접속한 운영자 한 명 때문에 사무실 운영자 화질까지 떨어지거나, 그 반대가 된다. "가장 느린 viewer에 맞춘다" 같은 정책을 정해 세션별 추정값을 모아서 하나로 결정하는 코드를 직접 넣어야 한다. 비트레이트 단위도 인코더마다 다르다. x264enc의 `bitrate`는 kbit/s, nvv4l2h264enc는 bit/s이고, v4l2h264enc에는 `bitrate` 속성이 없고 `extra-controls`로 준다. 혼잡 제어 원리는 [09장](/study/webrtc/09-quality-latency)에서 다뤘다.
3. <strong>첫 화면까지의 시간은 GOP가 정한다.</strong> DTLS가 끝나기 전 `writeFrame`은 `STATUS_SRTP_NOT_READY_YET`을 돌려준다. 그 뒤로도 다음 IDR이 올 때까지 viewer는 디코딩을 시작하지 못한다. GOP가 2초면 최악 2초를 더 기다린다. 새 세션이 연결될 때, 또는 viewer가 PLI를 보낼 때(`transceiverOnPictureLoss` 콜백) 인코더에 강제 키프레임을 요청하면 이 시간이 줄어든다. GStreamer에서는 `gst_video_event_new_upstream_force_key_unit()`으로 만든 upstream 이벤트를 인코더 쪽으로 보낸다. 샘플에는 이 처리가 없다.
4. <strong>지연이 쌓이지 않게 한다.</strong> CPU가 밀리면 큐에 프레임이 쌓여 지연이 계속 늘어난다. 인코더 앞 `queue`를 `leaky=downstream max-size-buffers=1`처럼 작게 두면 오래된 프레임을 버리고 최신 프레임을 보낸다. 샘플도 오디오 쪽에 `queue leaky=2 max-size-buffers=400`을 쓴다.
5. <strong>콜백은 GStreamer 스트리밍 스레드에서 돈다.</strong> 콜백 안에서 N개 세션의 `writeFrame`이 끝나야 다음 버퍼가 나온다. 콜백 안에서 블로킹 I/O나 긴 로그를 하지 않는다.
6. <strong>IP 카메라는 재인코딩을 피할 수 있다.</strong> 샘플의 `rtspsrc` 모드는 `uridecodebin`으로 디코딩한 뒤 x264enc로 다시 인코딩해서 CPU를 많이 쓴다. 카메라가 이미 B-프레임 없는 H.264를 낸다면 `rtspsrc ! rtph264depay ! h264parse config-interval=-1 ! video/x-h264,stream-format=byte-stream,alignment=au ! appsink`로 그대로 넘길 수 있다. 대신 비트레이트 적응은 포기해야 한다(카메라 인코더를 SDK가 조절할 수 없다). 카메라가 High 프로파일을 내면 SDP가 광고하는 `42e01f`와 어긋나므로 브라우저 디코딩 여부를 실기로 확인한다.

인제스트 모드 채널용으로 `kvsWebrtcStorageAudioVideoMaster`, `kvsWebrtcStorageVideoOnlyMaster`와 각 GstSample도 있다. `JoinStorageSession` API 문서는 "Both audio and video tracks are currently required"라고 적는데 SDK에는 비디오만 보내는 샘플이 있어 둘이 엇갈린다. 자세한 내용은 [21장](/study/webrtc/21-kvs-ingestion-storage)에서 다룬다.

## 4. AWS IoT Credential Provider로 임시 자격증명 받기

샘플은 `AWS_ACCESS_KEY_ID`·`AWS_SECRET_ACCESS_KEY` 환경변수로 동작하지만, 수천 대 농기계에 IAM 사용자의 장기 키를 심으면 한 대만 털려도 키를 돌려야 하고, 회전도 사실상 불가능하다. KVS는 인증서 인증을 지원하지 않고 SigV4만 받는다. 그래서 디바이스가 이미 가진 X.509 인증서로 AWS IoT credentials provider에 TLS 상호 인증을 하고, provider가 IAM 역할을 대신 assume해 임시 자격증명을 내주는 방식을 쓴다. MQTT로 IoT Core에 붙을 때 쓰는 그 인증서를 그대로 재사용한다. IoT 인증서·Thing·정책의 기본은 [AWS IoT Core 완전 정복](/posts/tech/2025-06-27-iot)에서 정리했다.

![AWS IoT Credential Provider 연동 흐름. 디바이스(X.509 인증서·개인키, Thing tractor-0017)가 ① x-amzn-iot-thingname 헤더를 붙여 IoT credentials provider 엔드포인트의 /role-aliases/{alias}/credentials에 mTLS GET을 보낸다. provider는 인증서에 붙은 IoT 정책의 iot:AssumeRoleWithCertificate를 확인하고 ② role alias가 가리키는 IAM 역할(신뢰 주체 credentials.iot.amazonaws.com)을 AssumeRole한다. ③ accessKeyId·secretAccessKey·sessionToken·expiration을 돌려받은 디바이스는 ④ SigV4로 KVS 시그널링에 Describe·GetEndpoint·GetIceServerConfig·ConnectAsMaster를 호출하고, 역할의 IAM 정책은 리소스를 channel/${credentials-iot:ThingName}/*로 제한한다](/images/study-webrtc/19-iot-credentials-light.png)
![AWS IoT Credential Provider 연동 흐름. 디바이스(X.509 인증서·개인키, Thing tractor-0017)가 ① x-amzn-iot-thingname 헤더를 붙여 IoT credentials provider 엔드포인트의 /role-aliases/{alias}/credentials에 mTLS GET을 보낸다. provider는 인증서에 붙은 IoT 정책의 iot:AssumeRoleWithCertificate를 확인하고 ② role alias가 가리키는 IAM 역할(신뢰 주체 credentials.iot.amazonaws.com)을 AssumeRole한다. ③ accessKeyId·secretAccessKey·sessionToken·expiration을 돌려받은 디바이스는 ④ SigV4로 KVS 시그널링에 Describe·GetEndpoint·GetIceServerConfig·ConnectAsMaster를 호출하고, 역할의 IAM 정책은 리소스를 channel/${credentials-iot:ThingName}/*로 제한한다](/images/study-webrtc/19-iot-credentials-dark.png)

### 설정 순서

<strong>1. IAM 역할 신뢰 정책</strong>(`trust.json`). credentials provider만 이 역할을 assume할 수 있다.

```json
{
  "Version": "2012-10-17",
  "Statement": {
    "Effect": "Allow",
    "Principal": { "Service": "credentials.iot.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }
}
```

<strong>2. 역할 권한 정책</strong>(`kvs-master.json`). C SDK README의 IoT 역할 예시에서 `CreateSignalingChannel`을 뺐다. 채널은 백엔드가 만든다는 전제다(20장). README도 기존 채널을 쓰면 이 권한을 빼도 된다고 적는다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kinesisvideo:DescribeSignalingChannel",
        "kinesisvideo:GetSignalingChannelEndpoint",
        "kinesisvideo:GetIceServerConfig",
        "kinesisvideo:ConnectAsMaster"
      ],
      "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/${credentials-iot:ThingName}/*"
    }
  ]
}
```

채널 ARN은 `channel/<채널이름>/<생성시각>` 형식이라 끝에 `/*`를 붙인다. 채널을 지웠다 같은 이름으로 다시 만들면 생성시각이 바뀌는데, 와일드카드라서 정책을 고칠 필요가 없다.

<strong>3. role alias, IoT 정책, 인증서 연결.</strong>

```bash
aws iam create-role --role-name KvsDeviceRole --assume-role-policy-document file://trust.json
aws iam put-role-policy --role-name KvsDeviceRole --policy-name kvs-master \
  --policy-document file://kvs-master.json

# 디바이스는 역할 ARN 대신 alias만 안다. 역할을 바꿔도 펌웨어를 고칠 필요가 없다
aws iot create-role-alias --role-alias KvsDeviceRoleAlias \
  --role-arn arn:aws:iam::123456789012:role/KvsDeviceRole \
  --credential-duration-seconds 3600

aws iot create-policy --policy-name KvsAssumeRoleWithCert --policy-document '{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "iot:AssumeRoleWithCertificate",
    "Resource": "arn:aws:iot:ap-northeast-2:123456789012:rolealias/KvsDeviceRoleAlias"
  }]
}'
aws iot attach-policy --policy-name KvsAssumeRoleWithCert --target <certificate-arn>
aws iot attach-thing-principal --thing-name tractor-0017 --principal <certificate-arn>

# 계정 전용 credentials provider 엔드포인트 (IoT 데이터 엔드포인트와 다르다)
aws iot describe-endpoint --endpoint-type iot:CredentialProvider
# → {"endpointAddress": "<prefix>.credentials.iot.ap-northeast-2.amazonaws.com"}
```

role alias 이름은 1~128자이고 영숫자와 `=`, `@`, `-`만 쓸 수 있다. `--credential-duration-seconds`는 최소 900초, 최대 43,200초(12시간), 기본 3,600초이며 IAM 역할의 최대 세션 시간보다 길 수 없다. role alias를 만드는 사용자에게는 그 역할에 대한 `iam:PassRole` 권한이 필요하다.

<strong>4. curl로 먼저 확인한다.</strong> SDK에 넣기 전에 디바이스에서 직접 호출해 보면 인증서·정책 문제를 SDK 로그 없이 가를 수 있다.

```bash
curl --cert certificate.pem.crt --key private.pem.key --cacert AmazonRootCA1.pem \
  -H "x-amzn-iot-thingname: tractor-0017" \
  https://<prefix>.credentials.iot.ap-northeast-2.amazonaws.com/role-aliases/KvsDeviceRoleAlias/credentials
# {"credentials":{"accessKeyId":"...","secretAccessKey":"...","sessionToken":"...","expiration":"..."}}
```

### SDK에 연결하기

샘플을 IoT 모드로 빌드하고 환경변수를 준다.

```bash
cmake .. -DIOT_CORE_ENABLE_CREDENTIALS=ON -DPARALLEL_BUILD=ON
make -j

export AWS_IOT_CORE_CREDENTIAL_ENDPOINT=<prefix>.credentials.iot.ap-northeast-2.amazonaws.com
export AWS_IOT_CORE_CERT=/etc/kvs/certificate.pem.crt
export AWS_IOT_CORE_PRIVATE_KEY=/etc/kvs/private.pem.key
export AWS_IOT_CORE_ROLE_ALIAS=KvsDeviceRoleAlias
export AWS_IOT_CORE_THING_NAME=tractor-0017
export AWS_DEFAULT_REGION=ap-northeast-2

./samples/kvsWebrtcClientMaster      # 인자가 없으면 AWS_IOT_CORE_THING_NAME을 채널 이름으로 쓴다
```

이 모드로 빌드하면 `AWS_ACCESS_KEY_ID` 같은 키 환경변수는 무시된다. 샘플 코드(`createSampleConfiguration`)를 보면 `AWS_IOT_CORE_CERTIFICATE_ID` 환경변수가 설정돼 있을 때 그 값으로 채널 이름을 덮어쓴다. 의도치 않게 이 변수가 남아 있으면 엉뚱한 채널로 붙으니 주의한다. `-DIOT_CORE_ENABLE_CREDENTIALS`는 샘플이 어떤 provider를 만들지 정하는 옵션일 뿐이다. 직접 작성한 앱에서는 2절 골격처럼 `createLwsIotCredentialProvider(endpoint, certPath, privateKeyPath, caCertPath, roleAlias, thingName, &provider)`를 부르면 된다.

provider는 받은 자격증명을 캐시하고 만료 전에 다시 받아 온다. producer-c의 `IotCredentialProvider.c`를 보면 만료 시각에서 남은 시간의 1~20%를 랜덤 지터로 빼서 유효 기간을 잡는다. 같은 시각에 켜진 디바이스 수천 대가 동시에 갱신 요청을 몰아 보내지 않게 하는 장치다.

### 정책 변수 `${credentials-iot:ThingName}`이 막아 주는 것

KVS `ConnectAsMaster` 문서에 따르면 같은 채널에 master가 두 번 붙으면 가장 최근 요청이 이기고 기존 연결 정보를 덮어쓴다([17장](/study/webrtc/17-kvs-architecture)). 디바이스 역할이 `channel/*`에 `ConnectAsMaster`를 허용하면, 인증서 하나가 유출됐을 때 그 인증서로 다른 농기계 채널의 master 자리를 빼앗아 가짜 영상을 내보낼 수 있다. 리소스를 `channel/${credentials-iot:ThingName}/*`로 묶으면 인증서마다 자기 Thing 이름과 같은 채널에만 접근한다. C SDK README도 "KVS recommendation is to use iot thing name as channel name"이라고 적는다.

이 변수에는 조건이 몇 가지 붙는다.

- `credentials-iot:ThingName`, `credentials-iot:ThingTypeName`, `credentials-iot:AwsCertificateId` 세 변수는 IAM 정책에서만 동작한다. IoT Core 정책에서는 쓸 수 없다.
- ThingName·ThingTypeName은 디바이스가 `x-amzn-iot-thingname` 헤더를 보낼 때만 채워진다. SDK의 provider는 `thingName` 인자로 이 헤더를 붙인다.
- 헤더의 Thing 이름이 인증서에 붙은 Thing과 다르면 403이 난다. 그래서 디바이스가 남의 Thing 이름을 사칭할 수 없다.
- 출처를 구분해 두면, 채널 리소스에 이 변수를 쓴 예시는 awslabs C SDK README에 있다. KVS 개발자 가이드(how-iot)의 예시는 스트림 리소스(`stream/${credentials-iot:ThingName}/*`)다.

::: warning Thing 이름과 채널 이름의 허용 문자가 다르다
IoT Thing 이름은 1~128자 `[a-zA-Z0-9:_-]+`, 시그널링 채널 이름은 1~256자 `[a-zA-Z0-9_.-]+`다. Thing 이름에 콜론(`:`)이 들어가면 같은 이름의 채널을 만들 수 없고, 채널 이름에 점(`.`)을 쓰면 같은 이름의 Thing을 만들 수 없다. Thing 이름 = 채널 이름 규칙을 쓰려면 이름을 `[a-zA-Z0-9_-]`, 128자 이하로 제한한다. 예: `tractor-0017`.
:::

<strong>시계가 맞지 않으면 아무것도 안 된다.</strong> mTLS 인증서 검증과 SigV4 서명 모두 정확한 시각이 필요하다. RTC 배터리가 없는 보드는 부팅 직후 1970년으로 시작해서 "certificate is not yet valid"로 TLS가 실패하거나 SigV4가 거부된다. systemd 환경이면 `systemd-time-wait-sync` 같은 장치로 NTP 동기화를 기다린 뒤 서비스를 띄운다. 임베디드 시계 동기 문제는 [13장](/study/webrtc/13-native-webrtc)에서도 다뤘다. SDK API는 인증서와 개인키를 파일 경로로 받으므로 개인키 파일 권한을 서비스 계정만 읽도록 제한한다.

## 5. 크로스 컴파일·리소스 제약·로그 레벨

### 크로스 컴파일

README에 따르면 SDK와 모든 의존성 빌드가 `CC`·`CXX` 환경변수를 따른다. 여기에 OpenSSL과 libsrtp의 대상 플랫폼을 알려 주는 세 변수를 더 준다.

```bash
export CC=aarch64-linux-gnu-gcc
export CXX=aarch64-linux-gnu-g++

cmake .. \
  -DBUILD_OPENSSL_PLATFORM=linux-aarch64 \
  -DBUILD_LIBSRTP_HOST_PLATFORM=x86_64-unknown-linux-gnu \
  -DBUILD_LIBSRTP_DESTINATION_PLATFORM=aarch64-unknown-linux-gnu \
  -DBUILD_STATIC_LIBS=TRUE \
  -DBUILD_SAMPLE=OFF \
  -DUSE_OPENSSL3=ON
make -j
```

`BUILD_OPENSSL_PLATFORM`은 OpenSSL `Configure`의 타깃 이름이고, libsrtp 두 변수는 빌드 호스트와 대상의 트리플릿이다. 위 값은 x86_64에서 aarch64 Linux로 빌드할 때의 예시다. README는 변수 이름만 적고, 구체적인 값은 매 커밋을 크로스 컴파일하는 자기들 CI 설정을 참고하라고 한다. 알려진 특수 사례도 README에 있다.

| 상황 | 옵션 |
|---|---|
| macOS M1에서 OpenSSL·libwebsockets 빌드 실패 | `-DBUILD_OPENSSL_PLATFORM=darwin64-arm64-cc` |
| 64비트 하드웨어 위 32비트 Raspbian 11 | `-DBUILD_OPENSSL_PLATFORM=linux-armv4` (OpenSSL이 64비트 ARM 어셈블리를 내지 않게) |
| uClibc 툴체인 | `-DADD_MUCLIBC` |
| 대상 보드에서 동작 검증 | `-DBUILD_TEST=TRUE` → 보드에서 `./tst/webrtc_client_test` |

GStreamer 샘플까지 크로스 빌드하려면 대상 보드의 GStreamer 개발 패키지가 든 sysroot를 `pkg-config`가 보게 해야 한다(`PKG_CONFIG_SYSROOT_DIR`, `PKG_CONFIG_LIBDIR`). 보통은 SDK만 크로스 빌드하고 GStreamer 연동 앱은 Yocto 레시피나 보드 위 네이티브 빌드로 만드는 편이 덜 고생스럽다.

### 메모리·CPU 조정

| 항목 | 기본값 | 조정 방법 |
|---|---|---|
| RTP rolling buffer(NACK 재전송용) | 3초, 비디오 5 Mibps · 오디오 1 Mibps, MTU 1,200 B | 트랜시버별 `configureTransceiverRollingBuffer` (0.1~10초, 100 Kibps~240 Mibps) |
| SDP m= 섹션 슬롯 | 5 | `-DMAX_SDP_SESSION_MEDIA_COUNT`. 슬롯당 스택 약 140 KB |
| 스레드 스택 | 시스템 기본 | `-DKVS_STACK_SIZE`, 개별 스레드는 `THREAD_CREATE_WITH_PARAMS()` |
| 스레드풀 | 꺼짐(켜면 최소 3, 최대 10) | `-DENABLE_KVS_THREADPOOL=ON`, `AWS_KVS_WEBRTC_THREADPOOL_MIN_THREADS`·`MAX_THREADS` |
| ICE 통계 계산 | 켜짐 | `-DENABLE_STATS_CALCULATION_CONTROL` + `enableIceStats = FALSE` |
| DTLS 인증서 | 연결마다 생성(저사양에서 5~15초) | 미리 생성 큐(`KVS_PRE_GENERATE_CERT_*`) |

rolling buffer 용량은 README 공식으로 "버퍼 시간 × 최고 비트레이트 / 8 / MTU"개의 RTP 패킷이다. README 예시처럼 1초 × 5 Mibps / 8 / 1,200 B면 546개다. 기본 3초면 비디오 트랜시버 하나에 약 1,638개 슬롯이고, 패킷이 MTU 크기로 꽉 찬다고 치면 상한이 약 2 MB다. 이게 viewer마다 하나씩 붙으니 viewer 10명이면 비디오 버퍼만 수십 MB까지 갈 수 있다. 실제 스트림이 1 Mbps라면 비트레이트 파라미터를 그만큼 낮춰 메모리를 아낀다. README는 너무 작게 잡으면 네트워크가 나쁠 때 NACK에 응답하지 못해 화면이 깨진다고 경고한다.

메모리나 CPU가 어디서 새는지 찾을 때는 `-DLINK_PROFILER=ON`으로 gperftools를 링크하고 `HEAPPROFILE=/tmp/heap.prof`나 `CPUPROFILE=/tmp/cpu.prof` 환경변수로 실행한다.

### 로그 레벨

`AWS_KVS_LOG_LEVEL`에 숫자로 준다. 기본은 WARN(4)이다.

| 값 | 레벨 | 용도 |
|---|---|---|
| 1 | VERBOSE | 함수 진입·탈출까지. `add_definitions(-DLOG_STREAMING)`과 함께 쓰면 매우 많다 |
| 2 | DEBUG | 개발 중 연결 문제 추적 |
| 3 | INFO | 현장 시험 |
| 4 | WARN | 기본값, 제품 기본 |
| 5 | ERROR | |
| 6 | FATAL | |
| 7 | SILENT | |
| 8 | PROFILE | 단계별 소요 시간 |

v1.8.0부터 SDK는 기본으로 연결 수립 단계별 소요 시간을 `build` 디렉터리의 `kvsFileLogFilter.x` 파일에 남긴다. 샘플의 `initSignaling`이 찍는 `[Signaling Get token] … ms`, `[Signaling Describe] … ms`, `[Signaling Connect] … ms` 같은 PROFILE 로그가 그것이다. "운영자가 버튼을 누르고 화면이 뜨기까지 왜 4초나 걸리나"를 따질 때 가장 먼저 볼 자료다. 일반 로그도 파일로 남기는 환경변수는 README 본문에 `AWS_ENABLE_FILE_LOGGING`, 환경변수 표에 `ENABLE_FILE_LOGGING`으로 이름이 엇갈려 적혀 있다. 쓰는 버전의 소스에서 확인한다.

현장 디버깅에 쓰는 스위치를 모아 두면 다음과 같다.

- `DEBUG_LOG_SDP=TRUE`: 주고받는 SDP를 출력한다. SDP에는 IP 주소와 `ice-pwd`가 들어 있으니 중앙 로그로 보내지 않는다.
- `KVS_ICE_TRANSPORT_POLICY=relay`: TURN 후보만 쓰게 강제한다. 방화벽 뒤 농장에서 TURN 경로가 열려 있는지 확인할 때 쓴다([07장](/study/webrtc/07-turn)).
- `samples/discoverNatBehavior.c`: 공개 API `discoverNatBehavior`로 현장 네트워크의 NAT 매핑·필터링 동작을 판별한다([05장](/study/webrtc/05-nat-stun)).
- ICE 타임아웃: 로그에 기본값(`iceLocalCandidateGatheringTimeout` 10,000 ms, `iceConnectionCheckTimeout` 12,000 ms, `iceCandidateNominationTimeout` 12,000 ms, 검사 주기 50 ms)이 찍힌다. LTE에서 relay 후보 수집이 느리면 `iceCandidateNominationTimeout`을 relay 수집 시간보다 길게 잡는다.
- 네트워크 인터페이스 필터: `KvsRtcConfiguration.iceSetInterfaceFilterFunc`로 `docker0`처럼 쓸모없는 인터페이스를 후보 수집에서 빼면 수집 시간이 준다.

### 방화벽에 열어야 할 것

농장 사무실이나 통신사 사설망은 아웃바운드도 막혀 있는 경우가 많다. README의 요구사항에 IoT 자격증명과 시각 동기를 더하면 다음과 같다.

| 대상 | 프로토콜·포트 | 예시 호스트 |
|---|---|---|
| KVS 컨트롤 플레인 | TCP 443 | `kinesisvideo.ap-northeast-2.amazonaws.com` |
| 채널 HTTPS 엔드포인트 | TCP 443 | `r-xxxxxxxx.kinesisvideo.<region>.amazonaws.com` |
| 채널 WSS 엔드포인트 | TCP 443 | `m-xxxxxxxx.kinesisvideo.<region>.amazonaws.com` |
| STUN | UDP 443 | `stun.kinesisvideo.<region>.amazonaws.com` |
| TURN | UDP/TCP 443 | `<ip>.t-xxxxxxxx.kinesisvideo.<region>.amazonaws.com` |
| IoT credentials provider | TCP 443 (mTLS) | `<prefix>.credentials.iot.<region>.amazonaws.com` |
| NTP | UDP 123 | 사내 또는 공용 NTP 서버 |

README는 공통 분모를 `*.kinesisvideo.<region>.amazonaws.com`의 443 포트로 요약한다. IPv6는 출처끼리 서술이 다르다. KVS System requirements 문서는 "IPv6 addresses aren't currently supported for STUN and TURN servers"라고 적는 반면, C SDK는 `KVS_DUALSTACK_ENDPOINTS=ON`으로 dual-stack 엔드포인트를 쓰고 IPv6 후보를 수집하는 옵션을 제공한다(`KVS_DISABLE_IPV4_TURN`, `KVS_DISABLE_IPV6_TURN`도 있다). SDK 쪽이 더 최근 변경일 가능성이 있지만, IPv6 전용망을 전제로 설계하기 전에 실측한다.

::: tip 핵심 정리
- KVS C SDK는 `kvsWebrtcClient`(WebRTC 스택)와 `kvsWebrtcSignalingClient`(KVS 시그널링)로 나뉘고, 자격증명·SigV4는 producer-c의 `kvsCommonLws`가 맡는다. 인코딩은 앱 몫이고 SDK는 인코딩된 프레임을 받아 보낸다.
- master 흐름은 credential provider → `createSignalingClientSync` → `signalingClientFetchSync` → `signalingClientConnectSync` → 오퍼마다 `createPeerConnection`·`addTransceiver`·`setRemoteDescription`·`setLocalDescription`·`createAnswer` → `writeFrame`이다.
- viewer마다 PeerConnection과 `writeFrame`이 하나씩 늘어 업링크·CPU·메모리가 viewer 수만큼 곱해진다. 인코더는 하나라서 세션별 대역폭 추정을 하나로 합치는 정책이 필요하다.
- GStreamer 연동은 `appsink` + `"new-sample"` 콜백이다. 캡스는 byte-stream·au·baseline, B-프레임 0, `h264parse config-interval=-1`, 타임스탬프는 버퍼 running time을 100 ns 단위로 쓴다.
- 디바이스 자격증명은 IoT credentials provider + role alias로 받고, IAM 정책 리소스를 `channel/${credentials-iot:ThingName}/*`로 묶어 인증서 하나가 다른 채널의 master를 빼앗지 못하게 한다. Thing·채널 이름은 `[a-zA-Z0-9_-]`로 제한한다.
- 시그널링 연결은 최대 1시간·idle 10분이 hard 한도이므로 재연결 감시 루프가 필수다. 부팅 직후에는 NTP 동기화를 기다린다.
:::

## 다음 챕터

[뷰어·백엔드 구현](/study/webrtc/20-kvs-viewer-backend)에서는 반대편인 운영자 브라우저를 JS SDK `SignalingClient`로 구현하고, 브라우저에 줄 자격증명을 Cognito Identity Pool·백엔드 STS 세션 정책·서명 URL 중 무엇으로 발급할지, 디바이스 등록과 함께 채널을 만들고 지우는 프로비저닝 백엔드를 어떻게 설계할지 다룬다.

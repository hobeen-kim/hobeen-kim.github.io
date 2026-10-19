---
title: "캡스톤: 농기계 원격 영상·제어 플랫폼"
description: "LTE·CGNAT 뒤 농기계 300대와 소수 운영자 브라우저를 KVS WebRTC·IoT Core·백엔드로 엮는 설계를 요구사항, 아키텍처, 시퀀스, ADR, 장애 시나리오, 비용 추정 순서로 정리하고 스터디 전체를 회고한다."
date: 2026-10-19
tags: [WebRTC, AWS, KVS, IoT, Architecture]
prev: /study/webrtc/24-ivs-real-time
next: /study/webrtc/appendix-glossary
---

# 캡스톤: 농기계 원격 영상·제어 플랫폼

::: info 학습 목표
- 농기계 원격 영상·제어의 기능·비기능 요구를 수치 목표로 바꾸고, 그 수치가 설계를 어떻게 제약하는지 설명할 수 있다.
- 디바이스·AWS·백엔드·브라우저 네 구역의 책임을 나누고, 영상·조작·신뢰 명령이 각각 어느 경로로 흐르는지 그릴 수 있다.
- 부팅부터 시청·조작·1시간 재연결까지의 시퀀스를 자격증명 수명과 함께 설명할 수 있다.
- 미디어 플랫폼, 녹화 방식, 제어 채널, 자격증명 발급의 네 가지 결정을 ADR 형식으로 근거와 함께 기록할 수 있다.
- 네트워크 열화·장애 시나리오마다 감지 신호와 대응을 정의하고, 가정을 명시한 월 비용을 계산할 수 있다.
:::

이 장은 새 개념을 소개하지 않는다. 앞의 24개 장에서 다룬 부품을 하나의 실제 시스템으로 조립하면서 <strong>"왜 이 부품을 이렇게 골랐는가"</strong>를 기록한다. 각 기술의 동작 원리는 해당 장 링크로 넘기고, 여기서는 선택지와 트레이드오프, 그리고 운영에서 무엇이 먼저 터지는지에 집중한다.

## 1. 요구사항

### 기능 요구

| 영역 | 요구 | 설계에 주는 제약 |
|---|---|---|
| 디바이스 | 농기계 300대(수백 대 규모). LTE 모뎀, 통신사 CGNAT 뒤. 카메라 1~2대. Jetson·라즈베리파이급 Linux 보드 | 공인 IP가 없어 인바운드 접속이 불가능하다. 디바이스가 먼저 밖으로 연결해 대기해야 한다([05장](/study/webrtc/05-nat-stun)) |
| 실시간 시청 | 운영자가 브라우저에서 기체를 골라 실시간 시청. 기체당 동시 시청 1~3명 | 1:소수 패턴이다. 수십~수천 명 방송은 요구하지 않는다 |
| 원격 조작 | 저속 이동(조그), 정지, 카메라 PTZ, 작업기 올림·내림 | 저지연이어야 하고, 링크가 끊기면 기체가 스스로 안전 측으로 가야 한다 |
| 명령·상태 | 미션 시작·중지, 설정 변경, 펌웨어 갱신, 텔레메트리 | 기체가 꺼져 있거나 음영 지역에 있어도 나중에 반영돼야 한다 |
| 녹화 | 비상정지·충돌 감지·운영자 표시 같은 사건의 전후 구간을 나중에 재생 | 상시 녹화 요구가 아니다. 사건 구간만 확실히 남기면 된다 |
| 보안 | 디바이스는 X.509 인증서로만 인증한다. 운영자는 담당 농장 기체만 볼 수 있다 | 디바이스에 장기 access key를 두지 않는다. 기체 단위 인가가 필요하다 |

::: warning 보드를 고르기 전에 하드웨어 인코더부터 확인한다
"Jetson·라즈베리파이급"이라는 말에는 함정이 있다. 라즈베리파이 4에는 하드웨어 H.264 인코더가 있지만 라즈베리파이 5에는 없다. Jetson 계열도 Orin Nano는 NVENC가 없어 CPU로 인코딩한다. 이 설계는 카메라 2대에 라이브용·녹화용 인코딩 세션을 따로 두므로(§4 ADR-2), <strong>하드웨어 인코더 유무와 동시 세션 수</strong>가 보드 선정의 첫 기준이다. 인코더 파이프라인은 [08장](/study/webrtc/08-rtp-codecs)과 [13장](/study/webrtc/13-native-webrtc)에서 다뤘다.
:::

### 비기능 요구

수치는 이 플랫폼에서 정한 설계 목표다. 표준이나 서비스가 보장하는 값이 아니다.

| 항목 | 목표 | 왜 이 값인가 |
|---|---|---|
| 영상 지연(glass-to-glass) | P2P p95 400 ms 이하, TURN 경유 p95 600 ms 이하 | G.114의 400 ms 권고([01장](/study/webrtc/01-why-webrtc))와 지연 예산 분해([09장](/study/webrtc/09-quality-latency)) |
| 조작 지연(입력 → 디바이스 적용) | p95 200 ms 이하 | 50Hz 조작 명령과 300 ms 워치독([11장](/study/webrtc/11-datachannel))보다 충분히 짧아야 오탐 정지가 없다 |
| 시청 시작 시간 | 클릭 → 첫 프레임 p95 3초 이하 | 자격증명 발급 + 시그널링 + ICE + 키프레임 대기의 합 |
| 신뢰 명령 반영 | 온라인 기체는 2초 이내, 오프라인 기체는 재접속 후 반영 | MQTT QoS 1 영구 세션과 Device Shadow |
| 화질 | 기본 720p 15~30fps, 열화 시 360p까지 단계 하강 | §5 비트레이트 사다리 |
| 동시 시청 | 기체당 3명(정책 상한) | KVS 기본 한도는 채널당 viewer 10명이지만, P2P라 LTE 업링크가 먼저 바닥난다 |
| 가용성 | 시청 기능 월 99.5%. 안전정지는 네트워크 상태와 무관하게 디바이스가 스스로 보장 | 원격 영상은 편의 기능이고, 안전은 디바이스의 책임이다 |
| 녹화 | 사건 전 5분 ~ 후 5분. 사건 후 30분 안에 재생 가능. 90일 보존 | LTE 업로드 시간을 고려한 값 |
| 보안 | 디바이스 장기 키 0개. 운영자 자격증명은 채널 1개, 수명 15분 | §4 ADR-4 |
| 비용 | AWS 월 $1,000 이하(300대). LTE 업링크 기체당 월 50 GB 이하 | §6 추정 |

비용 줄의 LTE 업링크 상한이 특히 중요하다. KVS WebRTC는 P2P라서 시청자 수만큼 디바이스가 영상을 따로 보낸다([16장](/study/webrtc/16-aws-landscape)). AWS 청구서보다 통신사 청구서가 먼저 상한에 걸리는 구조다. §6에서 숫자로 확인한다.

## 2. 전체 아키텍처

![전체 아키텍처 그림. 왼쪽 농기계 구역에는 카메라, HW 인코더, KVS C SDK(MASTER), IoT 에이전트, 안전 컨트롤러, 로컬 녹화가 있다. 가운데 AWS 구역에는 관리형 STUN/TURN, KVS 시그널링 채널, IoT Credential Provider, S3, IoT Core가 있고, 그 아래 백엔드 구역에는 채널 프로비저닝, 권한·시청 리스, STS 자격증명 발급, 명령·사건 API가 있다. 오른쪽 운영자 브라우저 구역에는 웹 콘솔, KVS JS SDK(VIEWER), RTCPeerConnection, 녹화 재생이 있다. 기기와 브라우저는 각각 WSS로 시그널링 채널에 붙고, 미디어와 DataChannel은 위쪽의 P2P 직결 경로로, 직결이 실패하면 점선의 TURN 릴레이 경로로 흐른다](/images/study-webrtc/25-architecture-light.png)
![전체 아키텍처 그림. 왼쪽 농기계 구역에는 카메라, HW 인코더, KVS C SDK(MASTER), IoT 에이전트, 안전 컨트롤러, 로컬 녹화가 있다. 가운데 AWS 구역에는 관리형 STUN/TURN, KVS 시그널링 채널, IoT Credential Provider, S3, IoT Core가 있고, 그 아래 백엔드 구역에는 채널 프로비저닝, 권한·시청 리스, STS 자격증명 발급, 명령·사건 API가 있다. 오른쪽 운영자 브라우저 구역에는 웹 콘솔, KVS JS SDK(VIEWER), RTCPeerConnection, 녹화 재생이 있다. 기기와 브라우저는 각각 WSS로 시그널링 채널에 붙고, 미디어와 DataChannel은 위쪽의 P2P 직결 경로로, 직결이 실패하면 점선의 TURN 릴레이 경로로 흐른다](/images/study-webrtc/25-architecture-dark.png)

| 구역 | 구성 요소 | 책임 | 관련 장 |
|---|---|---|---|
| 농기계 | 카메라 → HW 인코더 → KVS C SDK | 채널의 MASTER로 상시 대기하고, 시청 요청이 올 때만 PeerConnection을 만들어 송출 | [13장](/study/webrtc/13-native-webrtc), [19장](/study/webrtc/19-kvs-c-sdk) |
| 농기계 | IoT 에이전트 | 같은 인증서로 MQTT 연결. 신뢰 명령 수신, 텔레메트리 발행, Shadow 동기화 | [11장](/study/webrtc/11-datachannel) |
| 농기계 | 안전 컨트롤러 | DataChannel 조작 명령의 시퀀스·워치독 검사, CAN으로 기체 제어, 링크 단절 시 감속 → 정지 | [11장](/study/webrtc/11-datachannel) |
| 농기계 | 로컬 녹화 | 고화질 링 버퍼 유지, 사건 구간 S3 업로드 | §4 ADR-2 |
| AWS | IoT Credential Provider | 인증서 상호 TLS → role alias로 임시 자격증명 발급 | [19장](/study/webrtc/19-kvs-c-sdk) |
| AWS | KVS 시그널링 채널 | 기체당 1개, 채널 이름 = IoT thing 이름 | [17장](/study/webrtc/17-kvs-architecture), [18장](/study/webrtc/18-kvs-signaling-api) |
| AWS | 관리형 STUN/TURN | srflx 후보 수집, 직결 실패 시 릴레이 | [07장](/study/webrtc/07-turn), [17장](/study/webrtc/17-kvs-architecture) |
| AWS | IoT Core · S3 | MQTT 브로커·Shadow·Jobs·규칙, 사건 영상 보관 | [IoT Core 포스트](/posts/tech/2025-06-27-iot) |
| 백엔드 | 채널 프로비저닝 | 기체 등록 시 `CreateSignalingChannel`·태깅, 폐기 시 삭제 | [20장](/study/webrtc/20-kvs-viewer-backend), [22장](/study/webrtc/22-kvs-operations) |
| 백엔드 | 권한·시청 리스 | 운영자 ↔ 농장 ↔ 기체 ACL, 기체별 동시 시청 수 관리 | §4 ADR-4 |
| 백엔드 | STS 자격증명 발급 | 채널 ARN 하나로 좁힌 VIEWER 자격증명 발급 | [20장](/study/webrtc/20-kvs-viewer-backend) |
| 백엔드 | 명령·사건 API | 신뢰 명령을 IoT Core로 publish, 사건 인덱스·재생 URL 제공 | §4 ADR-3 |
| 브라우저 | KVS JS SDK + RTCPeerConnection | VIEWER 시그널링, 영상 수신, DataChannel 조작 | [02장](/study/webrtc/02-webrtc-api), [20장](/study/webrtc/20-kvs-viewer-backend) |

그림에서 바로 드러나지 않는 구조적 결정이 네 가지 있다.

<strong>첫째, 기체 1대 = 채널 1개이고 채널 이름은 IoT thing 이름이다.</strong> KVS C SDK README가 "iot thing name as channel name"을 권장하고, IAM 정책 변수 `${credentials-iot:ThingName}`을 쓰면 역할 하나로 300대가 각자 자기 채널만 쓰게 만들 수 있다. 카메라가 2대인 기체도 채널을 2개 만들지 않는다. 한 PeerConnection에 비디오 트랙 2개를 싣는다(C SDK에 `kvsWebrtcClientMaster_4Video_1Audio` 샘플이 있다). 그러면 ICE·DTLS 핸드셰이크와 TURN allocation이 하나로 끝나고 채널 요금도 절반이 된다. 보조 카메라는 기본적으로 저화질로 두고, 운영자가 DataChannel로 전환을 요청할 때만 올린다.

<strong>둘째, 디바이스는 채널을 만들지 않는다.</strong> C SDK README의 예시 IoT 역할 정책에는 `kinesisvideo:CreateSignalingChannel`이 들어 있다. 이 설계는 그것을 빼고, 채널 생성은 백엔드 프로비저닝이 맡는다. 펌웨어 버그나 탈취된 기체가 채널을 마구 만들어 할당량을 소진하는 일을 막고, 채널 수명을 기체 등록·폐기와 일치시킨다.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "kinesisvideo:DescribeSignalingChannel",
      "kinesisvideo:GetSignalingChannelEndpoint",
      "kinesisvideo:GetIceServerConfig",
      "kinesisvideo:ConnectAsMaster"
    ],
    "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/${credentials-iot:ThingName}/*"
  }]
}
```

이 정책은 role alias가 가리키는 IAM 역할에 붙인다. `${credentials-iot:ThingName}`은 IAM 정책에서만 동작하고, 디바이스가 `x-amzn-iot-thingname` 헤더를 보낼 때만 채워진다. 헤더의 thing 이름이 인증서에 붙은 thing과 다르면 403이 나므로, 기체가 남의 채널 이름을 사칭할 수 없다.

<strong>셋째, 제어는 두 경로로 나눈다.</strong> 시청 세션 안의 저지연 조작은 DataChannel(P2P), 세션과 무관하게 전달돼야 하는 신뢰 명령·상태·오프라인 큐는 MQTT(IoT Core)다. 역할 분담 원칙은 [11장](/study/webrtc/11-datachannel)의 DataChannel vs MQTT 표를 그대로 따르고, 명령별 배치는 §4 ADR-3에 적는다.

<strong>넷째, 운영자 브라우저는 IoT Core에 직접 붙지 않는다.</strong> 신뢰 명령은 백엔드 API를 거쳐 publish한다. 그래야 명령마다 인가와 감사 로그를 한곳에서 남길 수 있다. 텔레메트리 대시보드는 백엔드가 SSE나 WebSocket으로 내려준다([WebSocket 과 SSE](/posts/tech/2025-07-20-ssewebsocket)). 시청 중 영상 위에 겹치는 고빈도 오버레이(속도·조향각, 10Hz)만 DataChannel로 받는다.

## 3. 핵심 시퀀스: 부팅에서 원격 조작까지

![부팅, 시청·제어, 재연결 세 구간의 시퀀스 그림. 부팅 구간에서 농기계는 시계를 동기화한 뒤 IoT Credential Provider에 mTLS와 thingname 헤더로 요청해 기본 1시간짜리 임시 자격증명을 받고, KVS 시그널링 채널에 Endpoint(MASTER)·IceServerConfig를 거쳐 ConnectAsMaster로 대기한다. 시청 구간에서 브라우저는 백엔드에 OIDC 토큰으로 시청을 요청하고, 백엔드는 ACL과 시청 리스를 확인한 뒤 AssumeRole과 세션 정책으로 VIEWER 자격증명과 clientId를 돌려준다. 브라우저가 ConnectAsViewer 후 SDP_OFFER를 보내면 시그널링 채널이 농기계에 중계하고, SDP_ANSWER가 반대로 돌아오며, ICE_CANDIDATE가 양방향으로 trickle된 뒤 P2P 또는 TURN 경로로 영상과 DataChannel 제어가 흐른다. 재연결 구간에서는 약 40분마다 또는 GO_AWAY 수신 시 양쪽이 자격증명을 갱신하고 시그널링에 다시 연결한다](/images/study-webrtc/25-sequence-light.png)
![부팅, 시청·제어, 재연결 세 구간의 시퀀스 그림. 부팅 구간에서 농기계는 시계를 동기화한 뒤 IoT Credential Provider에 mTLS와 thingname 헤더로 요청해 기본 1시간짜리 임시 자격증명을 받고, KVS 시그널링 채널에 Endpoint(MASTER)·IceServerConfig를 거쳐 ConnectAsMaster로 대기한다. 시청 구간에서 브라우저는 백엔드에 OIDC 토큰으로 시청을 요청하고, 백엔드는 ACL과 시청 리스를 확인한 뒤 AssumeRole과 세션 정책으로 VIEWER 자격증명과 clientId를 돌려준다. 브라우저가 ConnectAsViewer 후 SDP_OFFER를 보내면 시그널링 채널이 농기계에 중계하고, SDP_ANSWER가 반대로 돌아오며, ICE_CANDIDATE가 양방향으로 trickle된 뒤 P2P 또는 TURN 경로로 영상과 DataChannel 제어가 흐른다. 재연결 구간에서는 약 40분마다 또는 GO_AWAY 수신 시 양쪽이 자격증명을 갱신하고 시그널링에 다시 연결한다](/images/study-webrtc/25-sequence-dark.png)

### ① 부팅: 시계가 맞아야 모든 것이 시작된다

부팅 직후 첫 작업은 네트워크 연결이 아니라 <strong>시계 동기화</strong>다. IoT Credential Provider와의 상호 TLS는 인증서 유효기간을 검사하고, KVS API는 SigV4 서명 시각을 검사한다. RTC 배터리가 없는 보드는 부팅 직후 시각이 1970년이거나 마지막 종료 시각에 멈춰 있다. 그대로 연결하면 TLS가 실패하거나 서명이 거부되는데, 로그에는 "인증 실패"로만 남아 원인을 찾기 어렵다([13장](/study/webrtc/13-native-webrtc)).

농기계에는 이 문제를 푸는 좋은 시간원이 이미 있다. 위치 측정용 <strong>GNSS 수신기</strong>다. chrony에 NTP와 GNSS(gpsd 경유)를 함께 시간원으로 등록하면, NTP가 막힌 망에서도 위성 신호만 잡히면 시계가 맞는다. 서비스는 동기화가 끝날 때까지 기다렸다가 시작한다.

시계가 맞으면 디바이스는 인증서로 Credential Provider의 `/role-aliases/<alias>/credentials`를 호출해 임시 자격증명을 받는다. role alias의 `credentialDurationSeconds`는 기본 3,600초(900~43,200초)다. 이어서 `DescribeSignalingChannel` → `GetSignalingChannelEndpoint(MASTER)` → `GetIceServerConfig` → `ConnectAsMaster` 순서로 시그널링 채널에 붙어 대기한다. 이 흐름은 C SDK를 `-DIOT_CORE_ENABLE_CREDENTIALS=ON`으로 빌드하면 SDK가 처리한다([19장](/study/webrtc/19-kvs-c-sdk)).

::: details 디바이스 서비스 설정 예 (환경 변수 + systemd)
```bash
# /etc/farm/kvs-master.env
AWS_DEFAULT_REGION=ap-northeast-2
AWS_IOT_CORE_CREDENTIAL_ENDPOINT=c1abcd2efgh3ij.credentials.iot.ap-northeast-2.amazonaws.com
AWS_IOT_CORE_CERT=/etc/farm/certs/device.pem.crt
AWS_IOT_CORE_PRIVATE_KEY=/etc/farm/certs/private.pem.key
AWS_IOT_CORE_ROLE_ALIAS=kvs-master-role-alias
AWS_IOT_CORE_THING_NAME=tractor-0042
AWS_KVS_CACERT_PATH=/etc/farm/certs/AmazonRootCA1.pem
```

```ini
# /etc/systemd/system/farm-kvs-master.service
[Unit]
Description=Farm KVS WebRTC master
After=network-online.target chrony.service
Wants=network-online.target

[Service]
EnvironmentFile=/etc/farm/kvs-master.env
# 시계 동기화 전에는 시작하지 않는다 (최대 30회 확인, 보정량 0.5초 이하)
ExecStartPre=/usr/bin/chronyc waitsync 30 0.5
ExecStart=/opt/farm/bin/farm-kvs-master tractor-0042
Restart=always
RestartSec=5
# 앱이 sd_notify(WATCHDOG=1)을 주기적으로 보내야 한다. 멈추면 systemd가 재시작한다
WatchdogSec=30

[Install]
WantedBy=multi-user.target
```

`farm-kvs-master`는 C SDK의 GStreamer 샘플(`kvsWebrtcClientMasterGstSample`)을 바탕으로 사내 파이프라인과 안전 컨트롤러 연동을 붙인 래퍼라고 가정한다.
:::

### ② 시청: 백엔드가 권한을 확인하고 채널 하나만 열어 준다

운영자가 기체를 클릭하면 브라우저는 백엔드에 시청 권한(view grant)을 요청한다. 백엔드는 세 가지를 확인한다. 이 운영자가 이 기체의 농장에 배정돼 있는가(ACL), 이 기체의 동시 시청 리스가 3개 미만인가, 그리고 기체가 온라인인가(Shadow reported 상태)다. 통과하면 STS `AssumeRole`에 세션 정책을 붙여 <strong>그 채널 ARN 하나에 대한 VIEWER 권한만 있는 15분짜리 자격증명</strong>을 발급한다(코드는 §4 ADR-4).

브라우저는 이 자격증명으로 `GetSignalingChannelEndpoint(VIEWER)`와 `GetIceServerConfig`를 호출하고 `ConnectAsViewer`로 붙는다. 그다음은 표준 JSEP 흐름이다([04장](/study/webrtc/04-sdp-jsep)). KVS 모델에서는 viewer가 offer를 만들고 master가 answer한다. 두 가지 구현 디테일이 시청 시작 시간을 좌우한다.

- <strong>DataChannel은 offer를 만들기 전에 생성한다.</strong> 그래야 첫 offer에 `m=application` 라인이 들어가 재협상 없이 조작 채널까지 한 번에 열린다([11장](/study/webrtc/11-datachannel)).
- <strong>첫 프레임은 키프레임을 기다린다.</strong> 연결 직후 브라우저가 PLI를 보내고 디바이스 인코더가 즉시 IDR을 만들게 한다. 인코더의 IDR 간격(예: 2초)에만 의존하면 첫 화면이 그만큼 늦어진다([09장](/study/webrtc/09-quality-latency)).

ICE 결과는 기체가 붙은 통신사의 CGNAT 동작에 달려 있다. 매핑이 endpoint-independent면 srflx 후보끼리 직결되고, 주소·포트 의존 매핑이면 TURN 릴레이로 간다([05장](/study/webrtc/05-nat-stun), [06장](/study/webrtc/06-ice)). 이 비율은 통신사·지역마다 달라서 실측해야 하고, §6에서 보듯 비용을 가장 크게 흔드는 변수다.

### ③ 유지와 재연결: 1시간 한도는 반드시 온다

KVS 시그널링 연결에는 조정할 수 없는 제약이 있다. 연결 최대 1시간, idle timeout 10분, `GO_AWAY` 이후 유예 60초다([18장](/study/webrtc/18-kvs-signaling-api)). 기체는 하루 종일 MASTER로 대기하므로 시그널링 재연결은 예외 처리가 아니라 정상 흐름이다.

| 대상 | 수명 | 갱신 시점 |
|---|---|---|
| 디바이스 임시 자격증명 | role alias 설정값(기본 3,600초) | 만료 전 여유를 두고 Credential Provider 재호출 |
| 시그널링 WSS 연결 | 최대 3,600초(`SessionExpiredException`에는 45분 서술도 있음) | 약 40분 + 기체별 무작위 지연(0~5분)에 계획 재연결([18장](/study/webrtc/18-kvs-signaling-api) 권장값), `GO_AWAY` 수신 시 즉시 |
| 브라우저 STS 자격증명 | 900초(`AssumeRole` 최솟값) | 캐시하지 않는다. 시그널링 재연결·ICE restart마다 백엔드에 새로 요청 |
| TURN 자격증명 | 300초(고정) | 새 PeerConnection·ICE restart마다 `GetIceServerConfig` 재호출. `RECONNECT_ICE_SERVER` 수신 시 새 ICE 서버로 ICE restart |

계획 재연결 시각에 무작위 지연을 섞는 이유는 300대가 같은 시각에 부팅했을 때 재연결이 한 순간에 몰리지 않게 하려는 것이다. 브라우저가 재연결할 때마다 백엔드에서 자격증명을 다시 받는 구조에는 부수 효과가 있다. <strong>권한 회수가 최대 15분 안에 반영된다.</strong> 운영자를 농장에서 빼면 다음 재연결 때 403이 난다.

시그널링이 끊기는 순간 이미 맺어진 PeerConnection의 미디어가 어떻게 되는지는 공식 문서에서 확인하지 못했다. 원리상 미디어는 시그널링과 별개 경로지만, 설계는 어느 쪽이든 견디게 만든다. 미디어가 살아 있으면 그대로 두고, `connectionState`가 `disconnected`나 `failed`로 가면 새 시그널링 연결 위에서 ICE restart offer를 보낸다.

```js
let signaling = null;
let plannedTimer = null;

async function connectSignaling(deviceId, onReady) {
  const res = await fetch(`/api/devices/${deviceId}/view-grants`, { method: 'POST' });
  if (res.status === 403) return showRevoked();            // ACL 회수가 여기서 반영된다
  if (res.status === 409) return showViewerFull(await res.json());
  if (!res.ok) throw new Error(`view-grant ${res.status}`);
  const grant = await res.json();
  const { wssEndpoint, iceServers } = await resolveEndpoints(grant); // 20장: Endpoint(VIEWER) + GetIceServerConfig

  const client = new KVSWebRTC.SignalingClient({
    channelARN: grant.channelArn,
    channelEndpoint: wssEndpoint,
    clientId: grant.clientId,            // 탭마다 고유해야 한다. 같은 clientId면 기존 연결이 밀려난다
    role: KVSWebRTC.Role.VIEWER,
    region: grant.region,
    credentials: grant.credentials,      // 채널 1개로 좁힌 15분짜리 STS 자격증명
    systemClockOffset: grant.serverTimeMs - Date.now(),
  });
  client.on('open', () => onReady(client, iceServers));
  client.on('close', () => {
    if (signaling !== client) return;    // 계획 재연결로 이미 교체된 연결
    scheduleRetry(deviceId, onReady);    // 지수 백오프
  });

  const previous = signaling;
  signaling = client;
  client.open();
  previous?.close();

  clearTimeout(plannedTimer);            // 1시간 한도 전에, 탭마다 흩어지게
  plannedTimer = setTimeout(() => connectSignaling(deviceId, onReady),
    40 * 60 * 1000 + Math.random() * 5 * 60 * 1000);
}
```

`systemClockOffset`에 백엔드가 응답에 실어 준 서버 시각을 쓰는 이유는 운영자 PC의 시계도 틀릴 수 있어서다. 브라우저의 SigV4 서명도 디바이스와 똑같이 시각 검사를 받는다.

## 4. 설계 결정 기록(ADR)

각 결정을 맥락·결정·근거·감수할 것·재검토 조건으로 남긴다. "감수할 것"과 "재검토 조건"이 ADR의 핵심이다. 1년 뒤 누군가 "왜 SFU를 안 썼지?"라고 물을 때, 당시의 가정이 아직 유효한지 바로 판단할 수 있어야 한다.

### ADR-1. 미디어 플랫폼: KVS WebRTC vs 직접 구축 vs IVS Real-Time

| 기준 | KVS WebRTC | 직접 구축(coturn + SFU) | IVS Real-Time |
|---|---|---|---|
| 토폴로지 | P2P, 직결 실패 시 관리형 TURN 릴레이 | SFU 경유, 디바이스 업링크 1회 | 서버 경유 publish/subscribe |
| 디바이스 쪽 구현 | C SDK(임베디드 Linux), IoT 인증서 연동 내장 | Pion·GStreamer·libwebrtc로 직접([13장](/study/webrtc/13-native-webrtc)) | Broadcast SDK는 Web·Android·iOS. Linux 보드는 WHIP 송출(H.264 Baseline, B-프레임 0) |
| 디바이스 인증 | 인증서 → Credential Provider → SigV4 | 토큰 발급을 직접 설계 | 백엔드가 participant token 발급 |
| 조작 데이터 | DataChannel(P2P) | SFU의 DataChannel 지원에 따름 | 범용 DataChannel은 확인되지 않음. 비디오에 싣는 SEI 메시지(1 KB 이하, 전달 보장 없음)만 있음 |
| 동시 시청 | 채널당 viewer 기본 10(조정 가능). 업링크가 시청자 수만큼 배수 | 사실상 SFU 용량까지 | subscriber 10,000(조정 가능), publisher 12 |
| 해상도·대역폭 | TURN 세션당 5 Mbps(조정 불가) | 자유 | publish 720p(조정 불가) |
| 과금 | 채널·메시지·TURN 분 + 릴레이 데이터 송신 | 인스턴스 + 트래픽 + 운영 인력 | participant-hour(호스트 포함, 접속 위치 기준 요율) |
| 운영 부담 | 낮음 | 높음(TURN·SFU 이중화, 패치, 인증서, 포트) | 낮음 |

| 항목 | 내용 |
|---|---|
| 상태 | 채택(2026-10) |
| 맥락 | 디바이스 1 : 시청자 1~3. LTE·CGNAT. 임베디드 C 환경. 플랫폼 운영 인력이 적다 |
| 결정 | <strong>KVS WebRTC</strong>(시그널링 채널 + 관리형 STUN/TURN)를 쓴다 |
| 근거 | ① 1:소수 패턴과 P2P 모델이 일치하고, 아무도 안 보면 미디어 비용이 0이다. ② C SDK와 IoT Credential Provider로 인증서 → 임시 자격증명 체인이 이미 있다. ③ 직결된 70%의 트래픽은 AWS를 거치지 않아 송신 요금이 붙지 않는다(§6). ④ TURN·시그널링 서버의 이중화와 패치를 직접 하지 않는다 |
| 감수할 것 | 업링크가 시청자 수만큼 배수가 된다. 시그널링을 1시간마다 다시 연결해야 한다. TURN 세션은 5 Mbps가 상한이다. P2P 모드에서는 서버 측 녹화·분석 지점이 없다 |
| 재검토 조건 | 기체당 동시 시청이 상시 4명 이상이 되거나, 수십 명 대상 방송(교육·시연·농장주 공개)이 필요하거나, 서버 측 실시간 영상 분석을 붙여야 할 때 |

직접 구축은 업링크 배수 문제를 SFU로 풀 수 있지만, 공인 IP·포트 범위·TLS 인증서를 갖춘 TURN 클러스터와 SFU 클러스터를 이중화해 운영해야 하고([07장](/study/webrtc/07-turn), [12장](/study/webrtc/12-topology-sfu)), 디바이스 인증 체계도 새로 만들어야 한다. IVS Real-Time은 호스트 혼자 있어도 participant로 과금하므로 기체가 상시 송출하면 안 되고, 시청 요청이 올 때만 publish를 시작하는 별도 제어 경로가 필요하다. 조작 명령도 전부 MQTT로 보내야 한다([24장](/study/webrtc/24-ivs-real-time)). Chime SDK는 참석자가 5분 연속 없으면 미팅이 자동 종료되는 회의 모델이라, 기체가 켜져 있는 내내 대기하는 구조와 맞지 않는다([23장](/study/webrtc/23-chime-sdk)).

### ADR-2. 녹화 방식: 저장 모드 vs 로컬 녹화 후 업로드 vs Producer SDK 병행

![녹화 방식 세 가지 비교 그림. A 저장 모드에서는 농기계와 최대 3명의 뷰어가 모두 AWS의 storage session에 relay로 붙고 storage session이 KVS Video Stream에 저장하며, 농기계와 뷰어 사이에 P2P가 없다. B 로컬 링 버퍼 방식에서는 농기계와 뷰어가 P2P로 연결되고, 농기계가 고화질을 별도로 인코딩해 eMMC·SSD 링 버퍼에 쓰다가 사건이 나면 S3로 업로드한다. C Producer SDK 병행 방식에서는 P2P를 유지하면서 농기계가 운용 중 상시 PutMedia로 KVS Video Stream에 송출한다](/images/study-webrtc/25-recording-options-light.png)
![녹화 방식 세 가지 비교 그림. A 저장 모드에서는 농기계와 최대 3명의 뷰어가 모두 AWS의 storage session에 relay로 붙고 storage session이 KVS Video Stream에 저장하며, 농기계와 뷰어 사이에 P2P가 없다. B 로컬 링 버퍼 방식에서는 농기계와 뷰어가 P2P로 연결되고, 농기계가 고화질을 별도로 인코딩해 eMMC·SSD 링 버퍼에 쓰다가 사건이 나면 S3로 업로드한다. C Producer SDK 병행 방식에서는 P2P를 유지하면서 농기계가 운용 중 상시 PutMedia로 KVS Video Stream에 송출한다](/images/study-webrtc/25-recording-options-dark.png)

| 기준 | A. 저장 모드 | B. 로컬 링 버퍼 + 사건 업로드 | C. Producer SDK 병행 |
|---|---|---|---|
| 실시간 경로 | <strong>P2P가 사라진다.</strong> 모든 피어가 storage session에 relay로 붙는다 | P2P 유지 | P2P 유지 |
| 시청자 수 | `JoinStorageSessionAsViewer` 최대 3명 | 정책상 1~3명 | 정책상 1~3명 |
| 조작 DataChannel | master 직결이 아니라서 전제할 수 없다(문서에서 확인 못 함) | 유지 | 유지 |
| 코덱·트랙 | H.264 + Opus. 문서상 오디오 트랙 필수(SDK에는 video-only 샘플이 있음) | 자유 | 자유 |
| 녹화 화질 | 실시간 화질 그대로. LTE가 열화되면 녹화도 열화 | 실시간 열화와 무관한 고정 고화질 | 별도 비트레이트 |
| LTE 업링크 | 세션 중 1배 | 사건 구간만 | 운용 시간 내내(예: 1 Mbps × 10시간 × 30일 = 135 GB/월) |
| 클라우드 비용 | 녹화 분 + 시청자 분 과금(§6 시나리오에서 월 약 $9,800) | S3 저장 수준 | KVS 수집 GB + 보존 |
| 기체 파손·도난 | 즉시 클라우드에 남음 | 업로드 전 구간은 유실 위험 | 즉시 클라우드에 남음 |
| 할당량·제약 | Media Storage Channels 기본 100(조정 가능), 세션 비트레이트 1 Mbps(조정 가능), 세션 1시간 | 없음 | 스트림 단위 |
| 적용 단위 | 채널 설정이라 켜는 순간 그 채널의 모든 연결이 바뀐다 | 기체 | 기체 |

::: warning 저장 모드는 "녹화 옵션"이 아니라 토폴로지 변경이다
`UpdateMediaStorageConfiguration`으로 저장을 켜면 문서 표현 그대로 "direct peer-to-peer (master-viewer) connections no longer occur"가 된다. 녹화 체크박스 하나 켰을 뿐인데 지연 경로, 시청자 상한, DataChannel 가용성, 과금 구조가 한꺼번에 바뀐다. 저장 세션 쪽 특성은 [21장](/study/webrtc/21-kvs-ingestion-storage)에서 다뤘다.
:::

| 항목 | 내용 |
|---|---|
| 상태 | 채택(2026-10) |
| 맥락 | 녹화는 사건 구간만 필요하다. 실시간 조작 경로(P2P + DataChannel)를 깨면 안 된다. LTE 데이터 상한이 있다. [21장](/study/webrtc/21-kvs-ingestion-storage)이 기본값으로 권한 "P2P 시청 + 병행 PutMedia"(이 표의 C)는 <strong>상시 녹화</strong>가 요구일 때의 결론이고, 운용 시간 내내 업링크를 쓴다. 그래서 21장이 그 변형으로 소개한 event 기반 녹화를 택하되, 업로드 대상을 KVS 스트림 대신 S3로 둔다 |
| 결정 | <strong>B. 디바이스 로컬 링 버퍼 + 사건 구간 업로드</strong>를 기본으로 한다. 무인 자율주행처럼 기체 파손 위험이 큰 모드에서만 C를 해당 모드 동안 켜는 선택지를 남긴다 |
| 근거 | ① P2P와 DataChannel을 그대로 유지한다. ② 녹화 화질이 LTE 열화와 무관하다. 사건은 대개 네트워크가 나쁠 때 일어난다. ③ LTE 업링크와 클라우드 비용이 사건 구간에만 든다 |
| 감수할 것 | 기체가 파손·도난되면 업로드 전 구간을 잃는다. 사건 직후 재생까지 업로드 시간(LTE에서 수 분)이 걸린다. 디바이스에 인코더 세션 2개와 업로드 에이전트가 필요하다 |
| 재검토 조건 | 규제·보험이 실시간 클라우드 증거 보존을 요구할 때, 사건 빈도가 높아 업로드량이 상시 송출과 비슷해질 때 |

디바이스 파이프라인은 카메라 출력을 두 갈래로 나눈다. 라이브 가지는 대역폭 추정에 따라 비트레이트를 바꾸고, 녹화 가지는 고정 고화질로 1분 조각을 써서 오래된 것부터 지운다. GStreamer `splitmuxsink`의 `max-size-time`·`max-files` 속성이 이 링 버퍼를 그대로 만들어 준다.

```text
v4l2src → tee ┬→ queue → [HW 인코더 #1: 적응 비트레이트, IDR 2초] → appsink → KVS C SDK (라이브)
              └→ queue → [HW 인코더 #2: 고정 4 Mbps] → h264parse → splitmuxsink (1분 조각 × 180개 = 3시간)
```

사건이 나면 업로드 에이전트가 해당 시각 전후 조각을 S3 presigned URL로 올린다. 재생을 빨리 해야 한다면 저화질 사본을 먼저, 고화질을 뒤이어 올리는 2단계 업로드가 쓸 만하다. 조각 파일 이름에는 GNSS로 맞춘 UTC 시각을 넣어, 사건 시각과 텔레메트리를 정확히 맞춘다.

### ADR-3. 제어 채널: DataChannel vs MQTT

| 명령·데이터 | 경로 | 옵션 | 이유 |
|---|---|---|---|
| 조그·PTZ 연속 조작(50Hz) | DataChannel `ctrl-rt` | `ordered: false`, `maxRetransmits: 0`, 시퀀스 번호 | 최신값만 유효하다. 재전송된 옛 명령은 해롭다 |
| 작업기 올림·내림, 라이트 같은 이산 명령 | DataChannel `ctrl-cmd` | reliable·ordered, 명령 ID + ack | 세션 중에만 의미가 있고 순서가 중요하다 |
| 비상정지 | DataChannel과 MQTT 동시 | 같은 명령 ID로 멱등 처리 | 어느 한 경로만 살아 있어도 도달해야 한다 |
| 미션 시작·중지, 모드 전환, 설정 변경 | MQTT QoS 1 + Shadow desired | 영구 세션 | 오프라인 큐, 감사 로그, 시청 여부와 무관 |
| 펌웨어 갱신, 로그 수집 | IoT Jobs | — | 대상 집합·진행률 관리 |
| 텔레메트리(저장용) | MQTT → IoT 규칙 | 5초 간격 | 시청 여부와 무관하게 이력이 남아야 한다 |
| 텔레메트리(영상 오버레이용, 10Hz) | DataChannel `telemetry` | unordered, 재전송 0 | 시청 중에만 필요하다 |
| 현재 시청 수·조작권 보유자 | Shadow reported / desired | — | 백엔드와 디바이스가 같은 상태를 본다 |

| 항목 | 내용 |
|---|---|
| 상태 | 채택(2026-10) |
| 결정 | <strong>세션 안 저지연 조작은 DataChannel, 세션 밖·신뢰·감사 대상은 MQTT, 비상정지는 둘 다</strong>로 보낸다 |
| 근거 | DataChannel은 시청 세션이 있을 때만 존재하지만 브로커를 거치지 않는 P2P라 가장 빠르다. MQTT는 상시 연결이고 영구 세션·Shadow·규칙 엔진으로 오프라인 전달과 감사를 준다([11장](/study/webrtc/11-datachannel), [MQTT 포스트](/posts/tech/2025-08-13-mqtt)) |
| 감수할 것 | 두 코드 경로와 명령 ID 중복 제거가 필요하다. 두 경로의 명령이 충돌할 때의 우선순위를 디바이스가 판정해야 한다 |
| 재검토 조건 | 시청 없이도 저지연 조작이 필요해질 때(예: 영상 없는 원격 조종기) |

여기에 두 가지 규칙을 더한다. 첫째, <strong>우선순위는 비상정지 > MQTT 모드 명령 > DataChannel 조작</strong>이다. 기체가 "원격 수동" 모드일 때만 DataChannel 조작 명령을 받는다. 미션 중지가 MQTT로 오면 진행 중인 조그 입력보다 먼저 적용된다. 둘째, <strong>시청자가 3명이어도 조작권은 1명</strong>이다. 백엔드가 조작권 리스를 한 운영자에게 주고 Shadow desired의 `controlOwner`에 그 viewer의 clientId를 적는다. master는 SDP offer의 `senderClientId`로 어느 PeerConnection이 누구인지 알기 때문에, `controlOwner`와 일치하는 PeerConnection의 DataChannel 명령만 안전 컨트롤러에 넘긴다.

### ADR-4. 운영자 자격증명 발급: Cognito Identity Pool vs STS 세션 정책

| 기준 | Cognito Identity Pool | 백엔드 STS `AssumeRole` + 세션 정책 | (변형) 백엔드가 서명 URL·ICE 서버까지 발급 |
|---|---|---|---|
| 브라우저가 받는 것 | Identity Pool 역할의 임시 자격증명 | 채널 ARN 하나로 좁힌 임시 자격증명 | presigned WSS URL과 ICE 서버 목록(자격증명 없음) |
| 기체 단위 인가 | 역할 정책으로 표현해야 한다. ACL이 바뀔 때마다 IAM 쪽 매핑을 맞춰야 한다 | 요청마다 백엔드가 DB의 ACL을 보고 채널 ARN을 정책에 넣는다 | 같음 |
| 권한 회수 반영 | 자격증명 만료까지 | 최대 15분 | URL·ICE 자격증명 유효 시간 |
| 백엔드 의존 | 없음(서버리스) | 시청 시작·재연결·ICE restart마다 호출 | 같음, 서명 로직이 추가됨 |
| 감사 | identity ID | `RoleSessionName`에 운영자 ID → CloudTrail에 남는 호출과 연결 | 백엔드 로그 |

| 항목 | 내용 |
|---|---|
| 상태 | 채택(2026-10) |
| 결정 | <strong>백엔드가 STS `AssumeRole` + 인라인 세션 정책으로 채널 1개·VIEWER 동작 4개·900초짜리 자격증명을 발급</strong>한다 |
| 근거 | 백엔드는 어차피 ACL과 시청 리스를 확인해야 한다. 그 자리에서 정확한 채널 ARN을 정책에 넣는 것이 가장 단순하다. 최종 권한은 기본 역할 정책과 세션 정책의 교집합이므로, 백엔드 버그로 정책 문자열이 넓어져도 기본 역할 범위를 넘지 못한다 |
| 감수할 것 | 시청 시작과 재연결이 백엔드 가용성에 의존한다. 브라우저에 자격증명이 15분간 존재한다 |
| 재검토 조건 | 브라우저에 자격증명을 전혀 두면 안 되는 보안 요구가 생기면 변형안으로 옮긴다 |

```kotlin
@Service
class ViewGrantService(
    private val sts: StsClient,
    private val acl: DeviceAclRepository,
    private val leases: ViewLeaseStore,
    @Value("\${farm.kvs.viewer-role-arn}") private val viewerRoleArn: String,
) {
    fun issue(operator: Operator, thingName: String): ViewGrant {
        val device = acl.findAccessibleDevice(operator.id, thingName)
            ?: throw AccessDeniedException("no access to $thingName")

        val clientId = "op-${operator.id}-${UUID.randomUUID().toString().take(8)}"
        if (!leases.tryAcquire(thingName, clientId, max = 3, ttl = Duration.ofMinutes(15))) {
            throw TooManyViewersException(thingName, leases.holders(thingName))  // → 409
        }

        val sessionPolicy = """
            {"Version":"2012-10-17","Statement":[{"Effect":"Allow",
              "Action":["kinesisvideo:DescribeSignalingChannel",
                        "kinesisvideo:GetSignalingChannelEndpoint",
                        "kinesisvideo:GetIceServerConfig",
                        "kinesisvideo:ConnectAsViewer"],
              "Resource":"${device.channelArn}"}]}
        """.trimIndent()

        val creds = sts.assumeRole {
            it.roleArn(viewerRoleArn)
                .roleSessionName("op-${operator.id}")
                .durationSeconds(900)
                .policy(sessionPolicy)
        }.credentials()

        return ViewGrant(device.channelArn, clientId, creds, serverTimeMs = System.currentTimeMillis())
    }
}
```

기본 역할(`viewer-role-arn`)에는 같은 4개 동작을 `channel/*`에 허용하고, 신뢰 정책으로 백엔드 역할만 assume할 수 있게 한다. 세션 정책의 평문 길이 한도는 2,048자라 채널 ARN 하나는 넉넉히 들어간다. clientId에 무작위 접미사를 붙이는 이유는 `ConnectAsViewer`가 같은 ClientId의 새 연결로 기존 연결을 대체하기 때문이다. 운영자가 탭을 두 개 열었을 때 서로를 밀어내지 않게 한다. ClientId는 `AWS_`로 시작할 수 없다는 제약도 있다([18장](/study/webrtc/18-kvs-signaling-api)).

## 5. 장애·네트워크 열화 시나리오

| 시나리오 | 감지 | 자동 대응 | 운영자 화면·후속 |
|---|---|---|---|
| LTE 대역폭 급락(셀 경계, 기지국 혼잡) | 디바이스: 송신 대역폭 추정 하락, RTCP 손실률·RTT 상승. 브라우저: `inbound-rtp`의 `framesDropped`·`jitterBufferDelay` 증가([15장](/study/webrtc/15-monitoring-debugging)) | 비트레이트 사다리를 즉시 한 단계 내린다. 보조 카메라부터 끈다. 10초 이상 안정되면 한 단계씩 올린다. 시청자가 n명이면 업링크 예산을 n으로 나눈다 | 화질 배지 표시. L4에서 저속 제한, L5 이하에서 수동 조작 잠금 |
| UDP 차단(일부 APN·사내망·공공 Wi-Fi) | UDP 후보 쌍의 connectivity check가 전부 실패. 선택된 쌍이 relay·TCP | KVS TURN의 TCP·TLS 443(`turns:`) 후보로 연결([07장](/study/webrtc/07-turn)). ICE가 2회 실패하면 브라우저가 `iceTransportPolicy: 'relay'`로 재시도 | TCP 위라 손실 시 HOL 지연이 생긴다. 사다리 상한을 L2로 낮추고 "TCP 릴레이" 표시 |
| 자격증명 만료 | 디바이스: KVS API 403·만료 오류, 만료 시각 타이머. 브라우저: 백엔드 grant 403 | 디바이스는 만료 전 여유를 두고 Credential Provider를 다시 호출. 브라우저는 재연결·ICE restart마다 새 grant를 받는다. TURN 자격증명(300초)은 새 PeerConnection마다 새로 받고, `RECONNECT_ICE_SERVER`를 받으면 ICE restart | grant 403은 권한 회수로 보고 "권한 없음" 표시. 재시도하지 않는다 |
| 시계 오차 | 부팅 직후 시각이 펌웨어 빌드 시각보다 과거. chrony offset 경보. SigV4 서명 시각 오류, TLS "not yet valid" | `chronyc waitsync`로 동기화 전 시작 금지. GNSS를 chrony 시간원으로 추가. 브라우저는 서버 시각으로 `systemClockOffset` 계산 | 기체 시계 상태를 Shadow reported로 보고해 대시보드에 표시 |
| 운영자 4명 이상 접속 | 백엔드 시청 리스 3개가 꽉 참. 디바이스가 Shadow에 보고한 PeerConnection 수 | 4번째 요청은 409로 거절하고 현재 시청자 목록을 돌려준다. 감독자 권한이면 가장 오래된 리스를 회수할 수 있다. 디바이스도 4번째 offer에 응답하지 않는다(KVS 기본 한도는 10이라 서비스가 막아 주지 않는다) | 초과 인원에게는 MQTT 스냅샷 보기를 제공한다. 상시 4명 이상이면 ADR-1 재검토 |
| 조작 중 제어 링크 단절(영상은 살아 있어도) | 50Hz 조작 명령 공백 300 ms | 안전 컨트롤러가 감속 → 정지 → 재무장 대기로 전환([11장](/study/webrtc/11-datachannel)) | 운영자가 데드맨 입력을 다시 해야 조작이 재개된다 |
| 디바이스 재부팅·프로세스 크래시 | 브라우저: `connectionState` `failed`, DataChannel close. 백엔드: IoT Core 수명 주기 이벤트(`$aws/events/presence/disconnected/+`) | systemd `Restart=always` + 하드웨어 워치독. 재부팅한 기체는 "원격 조작 비활성"으로 시작한다. master 재접속은 "가장 최근 연결이 이긴다"라서 좀비 연결이 남아 있어도 덮어쓴다 | 뷰어는 지수 백오프로 재연결하고 "기체 재시작 중" 표시 |
| 시그널링 1시간 한도·`GO_AWAY` | 연결 수명 타이머, `GO_AWAY` 메시지 | 40분 + 무작위 지연에 계획 재연결, `GO_AWAY`면 60초 유예 안에 재연결 | 미디어가 끊겼으면 새 시그널링 위에서 ICE restart |

![비트레이트 열화 사다리 그림. L0 카메라 2대 720p30 + 360p15(약 2.5 Mbps), L1 카메라 1대 720p30(약 2 Mbps), L2 720p15(약 1.2 Mbps), L3 480p15(약 600 kbps), L4 360p10(약 300 kbps), L5 MQTT 스냅샷 정지 화상, L6 영상 없음·텔레메트리만의 일곱 단계가 계단처럼 내려간다. 왼쪽에는 손실·RTT·대역폭이 악화되면 즉시 한 단계 내리고 10초 이상 안정되면 한 단계 올린다는 화살표가 있다. 오른쪽에는 L0~L3는 원격 수동 조작 허용, L4는 저속 제한 조작, L5~L6는 수동 조작 잠금(정지 명령만)이라는 권한 구간이 있다](/images/study-webrtc/25-degradation-ladder-light.png)
![비트레이트 열화 사다리 그림. L0 카메라 2대 720p30 + 360p15(약 2.5 Mbps), L1 카메라 1대 720p30(약 2 Mbps), L2 720p15(약 1.2 Mbps), L3 480p15(약 600 kbps), L4 360p10(약 300 kbps), L5 MQTT 스냅샷 정지 화상, L6 영상 없음·텔레메트리만의 일곱 단계가 계단처럼 내려간다. 왼쪽에는 손실·RTT·대역폭이 악화되면 즉시 한 단계 내리고 10초 이상 안정되면 한 단계 올린다는 화살표가 있다. 오른쪽에는 L0~L3는 원격 수동 조작 허용, L4는 저속 제한 조작, L5~L6는 수동 조작 잠금(정지 명령만)이라는 권한 구간이 있다](/images/study-webrtc/25-degradation-ladder-dark.png)

사다리의 단계별 비트레이트는 예시 값이다. 실제 값은 카메라·인코더·통신사별로 실측해 정한다. 설계에서 중요한 것은 세 가지다.

- <strong>내릴 때는 빠르게, 올릴 때는 느리게.</strong> 히스테리시스가 없으면 셀 경계에서 단계가 초 단위로 오르내리며 키프레임이 폭발하고, 그 키프레임이 다시 혼잡을 만든다. WebRTC 혼잡 제어 자체도 이렇게 동작하지만([09장](/study/webrtc/09-quality-latency)), 해상도·카메라 수 같은 큰 단위 전환은 애플리케이션이 결정해야 한다.
- <strong>최상단도 TURN 한도 아래에 둔다.</strong> L0의 합계 2.5 Mbps는 KVS TURN 세션 상한 5 Mbps 아래다. 카메라 2대를 한 PeerConnection에 싣는 설계(§2)라서 두 트랙이 한 TURN allocation을 공유한다는 점까지 고려한 값이다.
- <strong>영상 품질과 조작 권한을 묶는다.</strong> 360p10에 1초 가까운 지연으로 보이는 화면을 보고 5톤 트랙터를 조그하게 두면 안 된다. 단계와 측정 RTT를 조건으로 디바이스가 스스로 조작 권한을 낮추고, 운영자 화면은 그 상태를 보여주기만 한다. 권한 판정을 브라우저에 두면 조작된 클라이언트나 버그가 안전 장치를 우회할 수 있다.

## 6. 비용 추정

### 가정

| 가정 | 값 |
|---|---|
| 리전 | 서울(ap-northeast-2). 기체와 운영자가 모두 한국에 있어 TURN·시그널링 지연을 줄인다 |
| 가격 기준 | AWS Price List API 게시본. KVS 2026-09-30, 데이터 전송 2026-09-16, IoT Core 2026-10-03, IVS 2026-09-11. USD, 세금 제외 |
| 기체 수 | 300대. 매달 전부 한 번 이상 접속 → 활성 채널 300개 |
| 시청 시간 | 기체당 하루 평균 2시간(누군가 보고 있는 시간) × 30일 |
| 세션당 평균 시청자 | 1.5명 |
| 평균 세션 길이 | 15분 → 기체당 하루 8세션 |
| TURN 비율 | 시청자 연결의 30%가 릴레이. 릴레이 연결당 allocation 1개 |
| 평균 영상 비트레이트 | 1.2 Mbps(사다리 평균, 720p15 수준) → 릴레이 1분당 9 MB |
| 시그널링 메시지 | 시청자 연결당 100건(offer·answer + trickle candidate 양방향. 송신·수신 중 무엇을 세는지 확인하지 못해 둘 다 센 보수값) |
| 텔레메트리 | 기체당 5초에 1건(5 KB 이하), 하루 10시간 운용. IoT 규칙 1개, 액션 1개 |
| IoT 연결 | 24시간 상시 연결 |
| 사건 영상 | 기체당 월 2건 × 10분 × 4 Mbps → 월 약 180 GB |

여기서 나오는 물량은 다음과 같다.

- 세션 분: 300 × 120분 × 30일 = 1,080,000분
- 시청자 분: 1,080,000 × 1.5 = 1,620,000분
- TURN 분: 1,620,000 × 30% = 486,000분
- 시청자 연결 수: 300 × 8 × 30 × 1.5 = 108,000 → 시그널링 메시지 1,080만 건
- 릴레이 데이터: 486,000분 × 9 MB = 4,374 GB
- 텔레메트리: 300 × (36,000초 ÷ 5초) × 30일 = 6,480만 건
- IoT 연결 분: 300 × 1,440분 × 30일 = 1,296만 분

### 월 비용(서울)

| 항목 | 단가 | 물량 | 월 비용 |
|---|---|---|---|
| KVS 활성 시그널링 채널 | $0.04 / 채널 | 300 | $12.00 |
| KVS 시그널링 메시지 | $2.75 / 100만 건 | 1,080만 건 | $29.70 |
| KVS TURN 스트리밍 | $0.15 / 1,000분 | 486,000분 | $72.90 |
| 릴레이 데이터 인터넷 송신 | $0.126 / GB(첫 10 TB) | 4,374 GB | $551.12 |
| IoT Core 메시지 | $1.20 / 100만 건 | 6,480만 건 | $77.76 |
| IoT Core 규칙 실행 | $0.18 / 100만 건 | 6,480만 건 | $11.66 |
| IoT Core 액션 실행 | $0.18 / 100만 건 | 6,480만 건 | $11.66 |
| IoT Core 연결 | $0.096 / 100만 분 | 1,296만 분 | $1.24 |
| STS `AssumeRole` | 무료 | — | $0 |
| S3 사건 영상(약 180 GB) | 이 추정에서 단가 미확인 | — | 별도 |
| <strong>합계</strong> | | | <strong>약 $768(기체당 약 $2.56)</strong> |

데이터 전송은 매달 전역 합산 100 GB 무료 구간이 있지만 다른 서비스와 공유하므로 빼고 계산했다. TURN이 릴레이한 데이터가 AWS 밖으로 나가면 표준 데이터 전송 요금이 붙는다는 점이 [KVS 가격 페이지](https://aws.amazon.com/kinesis/video-streams/pricing/)의 WebRTC 예시에 명시돼 있다("You will incur standard AWS data transfer charges when you use TURN streaming to send data to destinations outside of AWS over the internet."). 단가 $0.126/GB는 Price List API `AWSDataTransfer` 서울 `APN2-DataTransfer-Out-Bytes`의 첫 10 TB 구간이다. TURN 분 요금만 보고 예산을 잡으면 이 줄을 통째로 놓친다.

### 무엇이 비용을 움직이는가

<strong>첫째, TURN 비율이 가장 큰 손잡이다.</strong> 30% 가정에서 릴레이 송신 요금이 전체의 72%를 차지한다. TURN 비율 r에 대해 월 비용은 대략 $144 + r × $2,080이다.

| TURN 비율 | TURN 분 | TURN 요금 | 릴레이 송신 | 월 합계 |
|---|---|---|---|---|
| 10% | 162,000 | $24.30 | 1,458 GB → $183.71 | $352.03 |
| 30% | 486,000 | $72.90 | 4,374 GB → $551.12 | $768.04 |
| 50% | 810,000 | $121.50 | 7,290 GB → $918.54 | $1,184.06 |

비용 상한 $1,000은 TURN 비율 약 41%에서 깨진다. 그래서 채널별 CloudWatch `TURNConnectedMinutes`를 대시보드에 올리고, TURN 비율이 35%를 넘으면 경보를 건다([22장](/study/webrtc/22-kvs-operations)). 줄이는 방법은 `iceTransportPolicy: 'relay'`를 기본값으로 두지 않기, 릴레이 연결에서는 사다리 상한을 한 단계 낮추기, 특정 통신사·지역에서 TURN 비율이 튀면 APN 설정을 점검하기다.

<strong>둘째, LTE 업링크가 AWS보다 먼저 상한에 닿는다.</strong> P2P라서 기체는 시청자마다 따로 보낸다. 기체당 월 업링크는 120분 × 30일 × 1.5명 × 9 MB = 48.6 GB로, 상한 50 GB에 거의 붙어 있다. 카메라 2대를 L0로 상시 보내면 두 배가 된다. 시청자 3명 상한과 보조 카메라 기본 저화질 정책은 품질 정책이면서 동시에 비용 정책이다.

<strong>셋째, 대안과 비교하면 P2P가 왜 싼지가 드러난다.</strong> 같은 시나리오를 다른 방식으로 돌리면 다음과 같다.

| 방식 | 계산 | 월 비용(추정) | 기체당 LTE 업링크 |
|---|---|---|---|
| 채택안: KVS P2P, TURN 30% | 위 표 | 약 $768 | 48.6 GB |
| KVS 저장 모드로 모든 시청 | 녹화 1,080,000분 × $0.0038 = $4,104 + 시청자 1,620,000분 × $0.0035 = $5,670 | 약 $9,774 + 스트림 수집·보존 + 채널·메시지·IoT | 32.4 GB(세션당 1회 송출) |
| IVS Real-Time(시청 중에만 publish) | (기체 18,000 + 시청자 27,000) participant-hour × 한국 요율 $0.125(첫 1만 시간), 이후 $0.118 구간 | 약 $5,380~5,625 + IoT | 32.4 GB |
| SFU 직접 구축(AWS 안) | 시청 트래픽 전부(1,620,000분 × 9 MB = 14,580 GB)가 인터넷 송신: 첫 10 TB $0.126 + 다음 구간 $0.122 | 송신만 약 $1,820 + 인스턴스·TURN·운영 인력 | 32.4 GB |

IVS 요율의 두 번째 구간 경계는 확인하지 못해 범위로 적었다. 저장 모드에서 릴레이 송신 요금이 따로 붙는지도 확인하지 못했다. 그래도 결론은 흔들리지 않는다. 서버를 경유하는 세 방식은 업링크를 1/1.5로 줄여 주지만 AWS 비용이 몇 배에서 열 배 넘게 뛴다. P2P의 비용 이점은 <strong>직결된 70%의 트래픽이 AWS를 전혀 거치지 않는다</strong>는 데서 나온다. 반대로 시청자가 늘어 업링크가 병목이 되는 순간 계산이 뒤집힌다. ADR-1의 재검토 조건이 바로 그 지점이다.

IoT Core 쪽은 텔레메트리 메시지가 대부분이다. 저장 목적 텔레메트리를 Basic Ingest(`$aws/rules/<규칙 이름>` 토픽)로 보내면 메시지 요금 없이 규칙·액션 요금만 붙어 월 약 $78을 줄일 수 있다. 다만 Basic Ingest 토픽은 다른 구독자에게 전달되지 않으므로, 실시간 구독이 필요한 상태 메시지는 일반 토픽으로 남긴다.

## 7. 마무리: 스터디 회고와 다음 단계

### 설계 요소와 근거가 된 장

| 설계 요소 | 근거가 된 장 |
|---|---|
| CGNAT 뒤 기체에 접속하는 방법(srflx, TURN, TCP·TLS 443) | [05](/study/webrtc/05-nat-stun) · [06](/study/webrtc/06-ice) · [07](/study/webrtc/07-turn) |
| viewer offer → master answer, offer 전에 DataChannel 생성, ICE restart | [03](/study/webrtc/03-signaling) · [04](/study/webrtc/04-sdp-jsep) · [11](/study/webrtc/11-datachannel) |
| 지연 목표, 비트레이트 사다리, 키프레임 정책 | [08](/study/webrtc/08-rtp-codecs) · [09](/study/webrtc/09-quality-latency) |
| 시그널링 인가가 곧 보안(채널 단위 자격증명, ACL) | [10](/study/webrtc/10-dtls-srtp) · [20](/study/webrtc/20-kvs-viewer-backend) |
| 제어 경로 분담, 워치독, 조작권 | [11](/study/webrtc/11-datachannel) |
| P2P를 고른 이유와 업링크 배수 | [12](/study/webrtc/12-topology-sfu) · [16](/study/webrtc/16-aws-landscape) |
| 디바이스 파이프라인, 시계, 인증서 | [13](/study/webrtc/13-native-webrtc) · [19](/study/webrtc/19-kvs-c-sdk) |
| 채널 구조, 시그널링 API, 연결 한도 | [17](/study/webrtc/17-kvs-architecture) · [18](/study/webrtc/18-kvs-signaling-api) |
| 녹화 방식 판단 | [21](/study/webrtc/21-kvs-ingestion-storage) |
| 관측 지표, 할당량, 비용 경보 | [15](/study/webrtc/15-monitoring-debugging) · [22](/study/webrtc/22-kvs-operations) |
| 대안 평가 | [14](/study/webrtc/14-whip-whep) · [23](/study/webrtc/23-chime-sdk) · [24](/study/webrtc/24-ivs-real-time) |

스터디를 마치며 남는 교훈은 세 가지다.

<strong>WebRTC 설계의 대부분은 WebRTC 바깥에 있다.</strong> `RTCPeerConnection` 호출 자체는 몇십 줄이면 끝난다. 이 장의 분량 대부분은 시그널링, 자격증명 수명, 재연결, 권한, 관측, 비용이었다. 표준이 시그널링을 비워 둔 이유([03장](/study/webrtc/03-signaling))가 곧 설계자가 채워야 할 몫이다.

<strong>P2P는 공짜가 아니라 비용을 디바이스 쪽으로 옮긴 것이다.</strong> 서버 비용과 지연은 줄지만, 업링크가 시청자 수만큼 늘고 서버 측 녹화·분석 지점이 사라진다. 1:소수에서는 좋은 거래이고 1:다수에서는 나쁜 거래다.

<strong>안전은 네트워크에 맡기지 않는다.</strong> 워치독, 재부팅 후 비무장 상태, 품질에 묶인 조작 권한은 모두 디바이스가 스스로 판정한다. 원격 영상·제어는 사람이 더 잘 판단하게 돕는 도구일 뿐, 링크가 끊긴 순간의 안전을 보장하는 수단이 아니다.

### 다음 단계

- <strong>1:N이 필요해지면 송출을 한 번으로 줄인다.</strong> 교육·시연이나 농장주 앱 공개처럼 시청자가 수십 명 이상이 되면, 기체가 SFU나 IVS Real-Time에 한 번만 올리고 서버가 복제하게 한다. 이때도 1:소수 조작 세션은 KVS P2P로 남기는 하이브리드가 자연스럽다. 조작은 지연이 중요하고, 방송은 규모가 중요하기 때문이다([12장](/study/webrtc/12-topology-sfu), [24장](/study/webrtc/24-ivs-real-time)).
- <strong>송출 프로토콜은 WHIP으로 표준화한다.</strong> WHIP은 2025년 3월 RFC 9725로 발행됐다. 디바이스가 WHIP으로 송출하면 IVS, 오픈소스 SFU, 다른 벤더 사이를 디바이스 코드 변경 없이 오갈 수 있다. 재생 쪽 WHEP는 2026년 10월 현재 아직 IESG 단계의 드래프트다([14장](/study/webrtc/14-whip-whep)).
- <strong>서버 측 영상 분석을 붙일 지점을 정한다.</strong> 실시간 분석이 필요하면 SFU에서 트랙을 분기하는 것이 자연스럽다. 사후 분석이면 사건 구간 S3 업로드나 저장 모드 스트림의 이미지 생성(GetImages)을 쓴다.
- <strong>코덱을 바꿔 LTE를 아낀다.</strong> C SDK 샘플은 H.265 인자를 받고, 차세대 보드는 AV1 하드웨어 인코더를 갖추기 시작했다. 같은 화질에 더 적은 비트레이트를 쓰면 §6의 LTE 상한에 여유가 생긴다. 다만 브라우저 디코딩 지원 범위를 먼저 확인해야 한다([08장](/study/webrtc/08-rtp-codecs)).
- <strong>디바이스 쪽 관측을 서버로 모은다.</strong> 디바이스의 송신 통계(대역폭 추정, 손실, 사다리 단계, TURN 여부)를 MQTT로 시계열 저장소에 보내면 통신사·지역별 TURN 비율과 열화 패턴이 보인다. 지표 설계는 [관측성 스터디](/study/observability/)의 방법론을 그대로 쓸 수 있다.

::: tip 핵심 정리
- 요구사항을 수치로 바꾸면 설계가 정해진다. 기체당 시청 3명 상한과 LTE 업링크 50 GB 상한이 P2P 채택, 사다리, 조작권 설계를 모두 제약했다.
- 구조는 기체 1대 = 채널 1개(이름 = thing 이름)다. 디바이스는 인증서 → Credential Provider로 자격증명을 받아 MASTER로 대기하고, 백엔드는 ACL을 확인한 뒤 채널 하나로 좁힌 15분짜리 STS 자격증명을 브라우저에 준다.
- 시그널링 1시간·TURN 자격증명 300초·브라우저 자격증명 900초라는 수명 차이 때문에 재연결은 정상 흐름이다. 계획 재연결에 무작위 지연을 섞고, 재연결 때마다 권한을 다시 확인한다.
- 녹화는 로컬 링 버퍼 + 사건 업로드로 한다. 저장 모드는 켜는 순간 P2P가 사라지는 토폴로지 변경이다. 제어는 세션 안 조작은 DataChannel, 신뢰 명령은 MQTT, 비상정지는 둘 다로 보낸다.
- 비용은 TURN 비율이 지배한다. 서울 기준 300대·하루 2시간 시청·TURN 30% 가정에서 월 약 $768이고, 그중 72%가 릴레이 데이터 송신이다. 서버 경유 대안은 업링크를 줄이는 대신 AWS 비용이 몇 배로 뛴다.
:::

## 다음 챕터

[용어집](/study/webrtc/appendix-glossary)에서는 이 스터디에 나온 WebRTC·NAT·RTP·KVS 용어를 한곳에 모아 짧은 정의와 해당 장 링크로 정리한다.

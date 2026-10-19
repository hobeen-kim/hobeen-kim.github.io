---
title: "KVS WebRTC 아키텍처"
description: "Kinesis Video Streams with WebRTC의 시그널링 채널·Master·Viewer·ClientId 모델, 관리형 STUN/TURN과 엔드포인트, GetSignalingChannelEndpoint부터 P2P/TURN 미디어까지의 연결 수립 순서, 조정할 수 없는 한도와 증설 가능한 한도, KVS Video Streams(Producer SDK)와의 관계를 정리한다."
date: 2026-10-19
tags: [WebRTC, AWS, Kinesis Video Streams, Signaling, TURN]
prev: /study/webrtc/16-aws-landscape
next: /study/webrtc/18-kvs-signaling-api
---

# KVS WebRTC 아키텍처

::: info 학습 목표
- 시그널링 채널, Master, Viewer, ClientId가 각각 무엇이고 어떤 제약을 갖는지 설명할 수 있다.
- KVS가 제공하는 HTTPS·WSS·STUN·TURN 엔드포인트의 형식과 포트를 알고, 방화벽 허용 목록을 작성할 수 있다.
- GetSignalingChannelEndpoint → GetIceServerConfig → WSS 연결 → SDP·ICE 중계 → P2P 또는 TURN 미디어로 이어지는 연결 수립 순서를 단계별로 설명할 수 있다.
- 조정할 수 없는 한도(연결 1시간, idle 10분, TURN 5 Mbps 등)와 증설 가능한 한도(viewer 수, 채널 수 등)를 구분하고 설계에 반영할 수 있다.
- KVS WebRTC와 KVS Video Streams(Producer SDK)가 같은 서비스 안의 다른 기능이라는 점과 둘을 잇는 지점을 안다.
:::

## 1. 구성 요소: 시그널링 채널·Master·Viewer·ClientId

KVS WebRTC의 중심 리소스는 <strong>시그널링 채널(Signaling Channel)</strong>이다. AWS 문서는 시그널링 채널을 "애플리케이션이 시그널링 메시지를 주고받아 peer-to-peer 연결을 발견·설정·제어·종료하게 해 주는 리소스"로 정의한다. 메시지에는 코덱과 코덱 파라미터 같은 로컬 미디어 정보, 그리고 연결 후보 경로(ICE candidate)가 담긴다. [03장](/study/webrtc/03-signaling)에서 직접 만든 WebSocket 시그널링 서버의 "방" 하나를 AWS가 대신 운영해 준다고 보면 된다. 다만 방의 모양이 정해져 있다. 구조는 master 1 : viewer 여러 명인 one-to-few 모델이다.

![KVS 시그널링 채널 모델. 위쪽에 KVS 관리형 시그널링 채널이 있고 디바이스(Master, 채널당 1)와 오른쪽의 브라우저 Viewer 세 명(ClientId op-1042-a7f3, op-2077-c91e, op-1042-0d2b)이 모두 점선 시그널링으로 채널에 연결된다. 미디어는 디바이스와 위쪽 두 Viewer 사이에 실선으로 직접 흐르고, 세 번째 Viewer는 아래쪽 KVS 관리형 STUN/TURN을 거치는 점선 relay로 연결된다. Viewer끼리는 서로 발견하거나 통신할 수 없다](/images/study-webrtc/17-channel-model-light.png)
![KVS 시그널링 채널 모델. 위쪽에 KVS 관리형 시그널링 채널이 있고 디바이스(Master, 채널당 1)와 오른쪽의 브라우저 Viewer 세 명(ClientId op-1042-a7f3, op-2077-c91e, op-1042-0d2b)이 모두 점선 시그널링으로 채널에 연결된다. 미디어는 디바이스와 위쪽 두 Viewer 사이에 실선으로 직접 흐르고, 세 번째 Viewer는 아래쪽 KVS 관리형 STUN/TURN을 거치는 점선 relay로 연결된다. Viewer끼리는 서로 발견하거나 통신할 수 없다](/images/study-webrtc/17-channel-model-dark.png)

채널에 붙는 피어는 역할이 둘이다.

| 항목 | Master | Viewer |
|---|---|---|
| 연결 API | `ConnectAsMaster` | `ConnectAsViewer` |
| 채널당 개수 | 1 (조정 불가) | 기본 10 (조정 가능) |
| 연결 쿼리 파라미터 | `X-Amz-ChannelARN` | `X-Amz-ChannelARN`, `X-Amz-ClientId` |
| 통신 대상 | 채널에 연결된 모든 viewer | master만. 다른 viewer는 발견할 수도 없다 |
| 같은 신원으로 다시 연결하면 | 가장 최근 요청이 이기고 기존 연결 메타데이터를 덮어쓴다 | 같은 ClientId의 새 연결이 기존 연결을 대체한다 |
| 한도 초과 시 | - | `ClientLimitExceededException` |
| 전형적인 주체 | 카메라 달린 디바이스(KVS C SDK) | 운영자 브라우저(JS SDK), 모바일 앱 |

<strong>ClientId</strong>는 viewer를 구분하는 이름이다. 길이는 1~256자이고 `AWS_`로 시작할 수 없다. master는 ClientId 없이 연결한다. 채널 안의 메시지에는 `senderClientId`와 `recipientClientId`가 붙는데, 둘 다 `[a-zA-Z0-9_.-]+` 패턴이다. master는 viewer가 여럿이므로 메시지를 보낼 때 받는 viewer의 ClientId를 반드시 지정해야 한다. viewer가 보내는 메시지는 `recipientClientId`가 무시되고 항상 master로 간다. viewer가 다른 viewer에게 보내는 메시지는 처리되지 않는다. ClientId를 어떻게 지을지는 [18장](/study/webrtc/18-kvs-signaling-api)에서 다룬다.

누가 SDP offer를 보내는지는 API가 고정하지 않는다. 문서는 master를 연결을 시작하는 피어로 설명하지만, 메시지 규칙만 보면 master는 어떤 viewer에게든 offer를 보낼 수 있고 viewer는 master에게만 보낼 수 있다. 공식 JS SDK 예제는 viewer가 채널에 연결되면 offer를 만들어 master에게 보내고, master가 answer를 돌려주는 흐름이다. C SDK의 master 샘플도 이 흐름에 맞춰 offer를 받으면 새 세션을 만든다. 이 스터디도 "viewer가 offer, master가 answer"를 기본으로 쓴다.

### 채널 속성

`CreateSignalingChannel`로 채널을 만들 때 정하는 속성은 많지 않다.

| 속성 | 값 | 비고 |
|---|---|---|
| `ChannelName` | 1~256자, `[a-zA-Z0-9_.-]+`, 계정·리전 안에서 유일 | 디바이스 식별자를 그대로 쓰는 경우가 많다 |
| `ChannelType` | `SINGLE_MASTER` | enum에는 `FULL_MESH`도 있지만 문서상 지원 타입은 `SINGLE_MASTER`뿐이다 |
| `SingleMasterConfiguration.MessageTtlSeconds` | 5~120초, 기본 60초 | 전달되지 않은 메시지를 버리기 전까지 보관하는 시간 |
| `Tags` | 0~50개 | 비용 배분, 디바이스·고객 단위 리소스 관리에 쓴다 |

채널을 만들면 ARN이 돌아온다. 형식은 `arn:aws:kinesisvideo:{region}:{account}:channel/{채널 이름}/{생성 시각}`이고, 마지막 숫자 때문에 같은 이름으로 지웠다 다시 만들면 ARN이 달라진다. 채널 상태는 `CREATING`, `ACTIVE`, `UPDATING`, `DELETING` 중 하나이고, 생성과 수정은 비동기다.

### 채널 설계 원칙

master가 채널당 하나라는 제약에서 설계 원칙 몇 가지가 바로 나온다.

- <strong>디바이스 하나에 채널 하나</strong>를 둔다. 카메라가 여러 대인 기계라면 한 master가 여러 비디오 트랙을 보내는 방법(C SDK에 `kvsWebrtcClientMaster_4Video_1Audio` 샘플이 있다)과 카메라마다 채널을 나누는 방법 중에서 고른다.
- <strong>채널 이름을 디바이스 신원과 맞춘다.</strong> C SDK README는 "KVS recommendation is to use iot thing name as channel name"이라고 권하고, IoT thing 이름 정책 변수로 채널 ARN을 제한하는 예시 정책을 싣는다. 이 정책은 [19장](/study/webrtc/19-kvs-c-sdk)에서 쓴다.
- <strong>master 중복 접속을 막는다.</strong> 같은 채널에 master가 두 번 붙으면 마지막 연결이 이긴다. 디바이스 앱이 재시작되는 동안 이전 프로세스가 살아 있거나, 같은 인증서를 쓰는 디바이스 두 대가 같은 채널에 붙으면 서로를 밀어내며 연결이 흔들린다. 프로세스 단일 실행 보장과 디바이스별 신원 분리가 필요하다.

## 2. 관리형 STUN/TURN과 엔드포인트

KVS는 시그널링뿐 아니라 STUN과 TURN도 운영한다. [05장](/study/webrtc/05-nat-stun)과 [07장](/study/webrtc/07-turn)에서 직접 띄우던 서버를 AWS가 맡는 셈이다. 클라이언트가 닿아야 하는 엔드포인트는 다음과 같다. KVS 개발자 가이드의 System requirements 문서 원문 형식이다.

| 용도 | 형식 | 비고 |
|---|---|---|
| HTTPS API | `https://*.kinesisvideo.{region}.amazonaws.com` | 컨트롤 플레인과 채널 HTTPS 엔드포인트 |
| WSS 시그널링 | `wss://*.kinesisvideo.{region}.amazonaws.com` | 채널 WSS 엔드포인트 |
| STUN | `stun:stun.kinesisvideo.{region}.amazonaws.com:443` | API로 받지 않고 문자열을 직접 넣는다 |
| TURN | `turn:_._.kinesisvideo.{region}.amazonaws.com:443`, `turns:_._.kinesisvideo.{region}.amazonaws.com:443` | 실제 URI·자격증명은 `GetIceServerConfig`로 받는다 |

TURN의 `_._.`는 문서 원문에 그렇게 적혀 있다. 와일드카드 호스트를 표기한 것으로 보이지만 문서가 따로 설명하지는 않는다. 실제 호스트 예시는 C SDK README의 "Outbound hostname and port requirements"에 있다.

| 엔드포인트 | 프로토콜·포트 | 예시 호스트 |
|---|---|---|
| KVS 컨트롤 플레인 | TCP 443 | `kinesisvideo.us-west-2.amazonaws.com` |
| 채널 HTTPS 엔드포인트 | TCP 443 | `r-2c136a55.kinesisvideo.us-west-2.amazonaws.com` |
| 채널 WSS 엔드포인트 | TCP 443 | `m-26d02974.kinesisvideo.us-west-2.amazonaws.com` |
| STUN | UDP 443 | `stun.kinesisvideo.us-west-2.amazonaws.com` |
| TURN | UDP·TCP 443 | `34-219-91-62.t-1cd92f6b.kinesisvideo.us-west-2.amazonaws.com:443` |

README는 "hostname의 최소 공통 분모는 `*.kinesisvideo.<region>.amazonaws.com`이고 포트는 443"이라고 정리한다. 방화벽 허용 목록은 이 와일드카드와 TCP·UDP 443으로 만들면 된다. 모든 트래픽이 443을 쓴다는 점은 디바이스 쪽에 유리하다. 통신사 망이나 고객사 방화벽이 UDP를 막더라도 TURN over TCP·TLS(443)로 우회할 길이 남는다. 지연은 늘어나지만 끊기는 것보다 낫다([07장](/study/webrtc/07-turn)).

### TURN 자격증명과 한도

TURN 자격증명은 `GetIceServerConfig`가 돌려주는 `IceServerList`에 들어 있다. 항목마다 `Uris`, `Username`, `Password`, `Ttl`이 있고, `Uris`는 I-D.petithuguenin-behave-turn-uris 형식이다. 이 형식은 [07장](/study/webrtc/07-turn)의 시간제한 credential REST 패턴과 같은 계열이다. `?transport=udp` 같은 쿼리가 붙은 실제 응답 예시는 공식 문서에서 확인하지 못했으므로, 운영 전에 응답을 직접 찍어 확인해야 한다.

| 항목 | 값 | 조정 |
|---|---|---|
| TURN 자격증명 수명 | 300초(5분) | 불가 |
| TURN 세션당 대역폭 | 5 Mbps | 불가 |
| 시그널링 채널당 동시 TURN allocation | 50 | 불가 |

자격증명 수명은 문서끼리 표기가 다르다. API Reference는 `IceServer.Ttl`을 "Fixed value of 300"으로, Quota 표는 "Credential Lifecycle 5 minutes"로 적는다. 반면 AWS CLI 레퍼런스는 Ttl 제약을 "min: 30, max: 86400"으로 적는다. 서비스가 실제로 돌려주는 값은 API Reference와 Quota 기준인 300초로 보고 설계하는 편이 안전하다. 즉 `GetIceServerConfig` 결과를 오래 캐시하면 안 되고, 새 PeerConnection을 만들 때마다 새로 받아야 한다. C SDK는 ICE 설정 만료 30초 전부터 갱신하도록 구현돼 있다.

### IPv6 서술 충돌

System requirements 문서에는 "IPv6 addresses aren't currently supported for STUN and TURN servers."라는 Note가 있다. 그런데 SDK 쪽은 이미 dual-stack을 지원한다. JS SDK README는 dual-stack 모드 STUN을 `stun:stun.kinesisvideo.${region}.api.aws:443`로 안내하고, C SDK v1.20.0은 `KVS_DUALSTACK_ENDPOINTS=ON`으로 dual-stack을 켜면 IPv6 candidate 수집을 시도한다. 문서마다 다르므로 SDK 쪽이 더 최신일 가능성이 높다. IPv6 전용 망(일부 LTE 사설 APN)에 디바이스를 둘 계획이라면 대상 리전에서 실제로 검증해야 한다.

## 3. 연결 수립 시퀀스

이제 디바이스(master)와 운영자 브라우저(viewer)가 연결되는 과정을 처음부터 끝까지 따라가 보자.

![KVS WebRTC 연결 수립 시퀀스. 다섯 참여자는 디바이스(Master), KVS API(kinesisvideo), 채널 HTTPS 엔드포인트, 채널 WSS 엔드포인트, 브라우저(Viewer)다. ① Master가 GetSignalingChannelEndpoint(MASTER)로 WSS·HTTPS 엔드포인트를 받고, ② HTTPS 엔드포인트에 GetIceServerConfig를 호출해 TTL 300초짜리 TURN URI·자격증명을 받고, ③ SigV4 서명 URL로 ConnectAsMaster한다. ④ Viewer도 GetSignalingChannelEndpoint(VIEWER)와 GetIceServerConfig를 호출하고 ⑤ ClientId를 넣어 ConnectAsViewer한다. ⑥ Viewer의 SDP_OFFER가 WSS 엔드포인트를 거쳐 senderClientId와 함께 Master에 전달되고, ⑦ Master의 SDP_ANSWER가 recipientClientId로 Viewer에게 전달된다. ⑧ ICE_CANDIDATE가 채널을 거쳐 양방향으로 오가고, ⑨ ICE 연결 확인, DTLS, SRTP 미디어가 직결 또는 TURN relay로 흐른다](/images/study-webrtc/17-connection-sequence-light.png)
![KVS WebRTC 연결 수립 시퀀스. 다섯 참여자는 디바이스(Master), KVS API(kinesisvideo), 채널 HTTPS 엔드포인트, 채널 WSS 엔드포인트, 브라우저(Viewer)다. ① Master가 GetSignalingChannelEndpoint(MASTER)로 WSS·HTTPS 엔드포인트를 받고, ② HTTPS 엔드포인트에 GetIceServerConfig를 호출해 TTL 300초짜리 TURN URI·자격증명을 받고, ③ SigV4 서명 URL로 ConnectAsMaster한다. ④ Viewer도 GetSignalingChannelEndpoint(VIEWER)와 GetIceServerConfig를 호출하고 ⑤ ClientId를 넣어 ConnectAsViewer한다. ⑥ Viewer의 SDP_OFFER가 WSS 엔드포인트를 거쳐 senderClientId와 함께 Master에 전달되고, ⑦ Master의 SDP_ANSWER가 recipientClientId로 Viewer에게 전달된다. ⑧ ICE_CANDIDATE가 채널을 거쳐 양방향으로 오가고, ⑨ ICE 연결 확인, DTLS, SRTP 미디어가 직결 또는 TURN relay로 흐른다](/images/study-webrtc/17-connection-sequence-dark.png)

<strong>① 엔드포인트 조회.</strong> master는 컨트롤 플레인의 `GetSignalingChannelEndpoint`를 호출한다. 요청에는 채널 ARN과 `SingleMasterChannelEndpointConfiguration { Protocols: [WSS, HTTPS], Role: MASTER }`를 넣는다. 응답은 프로토콜별 엔드포인트 목록이다. 문서는 "master와 viewer의 연결 엔드포인트가 따로 있다"고 적으므로 Role을 정확히 넣어야 한다.

<strong>② ICE 서버 조회.</strong> ①에서 받은 HTTPS 엔드포인트로 `GetIceServerConfig`를 호출해 TURN 자격증명을 받는다. JS SDK README는 HTTPS 엔드포인트가 ICE 서버를 받을 때만 쓰이고, 실제 시그널링은 WSS 엔드포인트로 한다고 설명한다. STUN은 이 API로 받지 않는다. `stun:stun.kinesisvideo.{region}.amazonaws.com:443` 문자열을 TURN 목록과 함께 `iceServers`에 넣는다.

<strong>③ master 연결.</strong> WSS 엔드포인트에 `X-Amz-ChannelARN` 쿼리를 붙이고 SigV4로 서명한 URL로 WebSocket을 연다. KVS는 인증서 기반 인증을 받지 않고 SigV4만 받으므로, 디바이스도 IAM 자격증명이 있어야 한다. 디바이스에 장기 키를 심지 않으려면 AWS IoT Credential Provider로 임시 자격증명을 받는다([19장](/study/webrtc/19-kvs-c-sdk)). 서명 URL을 만드는 방법은 [18장](/study/webrtc/18-kvs-signaling-api)에서 본다.

<strong>④·⑤ viewer 준비와 연결.</strong> viewer도 같은 두 API를 Role `VIEWER`로 호출한 뒤, `X-Amz-ClientId`를 추가한 서명 URL로 연결한다. 브라우저에 AWS 자격증명을 두지 않으려면 이 단계 전체를 백엔드가 대신 하고 결과만 넘겨줄 수 있다([20장](/study/webrtc/20-kvs-viewer-backend)).

<strong>⑥·⑦ SDP 교환.</strong> viewer가 `SDP_OFFER`를 보내면 KVS가 master에게 전달하면서 `senderClientId`에 viewer의 ClientId를 채운다. master는 그 값을 `recipientClientId`로 넣어 `SDP_ANSWER`를 돌려준다. 아직 전달되지 않은 offer가 있는 상태에서 같은 대상에게 새 offer가 오면 기존 것을 덮어쓴다. 받는 쪽이 잠시 연결돼 있지 않으면 메시지는 `MessageTtlSeconds` 동안 보관됐다가 버려진다.

<strong>⑧ ICE candidate 교환.</strong> 양쪽은 후보를 모으는 대로 `ICE_CANDIDATE`로 보낸다(Trickle ICE, [06장](/study/webrtc/06-ice)). host 후보, KVS STUN으로 얻은 srflx 후보, KVS TURN으로 얻은 relay 후보가 모두 채널을 거쳐 오간다.

<strong>⑨ 미디어.</strong> ICE 연결 확인이 성공한 후보 쌍으로 DTLS 핸드셰이크를 하고 SRTP 미디어가 흐른다([10장](/study/webrtc/10-dtls-srtp)). 직결 후보 쌍이 하나도 성공하지 못하면 relay 후보 쌍이 선택되고, 미디어는 KVS TURN을 거친다. 어느 경우든 미디어는 시그널링 채널을 지나지 않는다.

이 순서에서 운영상 중요한 점은 <strong>①~③을 누가 언제 하느냐</strong>다. 디바이스가 부팅하자마자 ①~③을 끝내고 채널에 붙어 있으면, 운영자가 "영상 보기"를 누른 순간부터의 대기 시간은 ④~⑨만 남는다. 반대로 운영자 요청을 받은 뒤에 디바이스를 깨워 ①~③부터 하면 그만큼 첫 화면이 늦어진다. 그래서 디바이스는 시그널링 연결을 상시 유지하는 편이 좋다. 다만 4절의 연결 1시간 한도 때문에 "상시 유지"는 "1시간 안에 주기적으로 다시 연결"을 뜻한다.

## 4. 할당량: 고정 한도와 증설 가능 한도

KVS WebRTC 할당량은 Service Quotas 기준으로 두 부류로 나뉜다. 조정할 수 없는 한도는 아키텍처가 맞춰야 하는 제약이고, 조정 가능한 한도는 증설 요청으로 풀리는 운영 문제다.

| 구분 | 항목 | 값 | 설계에 미치는 영향 |
|---|---|---|---|
| 조정 불가 | master 연결 수 | 채널당 1 | 디바이스당 채널 1개, 중복 master 방지 |
| 조정 불가 | 최대 연결 시간 (`ConnectAsMaster`/`ConnectAsViewer`) | 1시간(3,600초) | 장시간 디바이스는 1시간 안에 재연결 로직 필수 |
| 조정 불가 | 최대 idle timeout | 10분(600초) | 메시지가 없는 연결은 끊긴다 |
| 조정 불가 | `GO_AWAY` 이후 유예 | 1분(60초) | 신호를 받으면 1분 안에 재연결 |
| 조정 불가 | `ConnectAsMaster`/`ConnectAsViewer` 요청률 | 채널당 3 TPS | viewer 동시 재접속 시 백오프 필요 |
| 조정 불가 | `SendSdpOffer`/`SendSdpAnswer` | WebSocket 연결당 5 TPS | 짧은 시간에 재협상을 반복하지 않는다 |
| 조정 불가 | `SendIceCandidate` | WebSocket 연결당 20 TPS | 후보가 한꺼번에 많이 나오면 걸린다 |
| 조정 불가 | 메시지 payload | 10 KB | base64 인코딩 후 크기 기준 |
| 조정 불가 | `DescribeSignalingChannel`/`GetSignalingChannelEndpoint` | 계정 300 TPS, 채널당 5 TPS | 대량 동시 부팅 시 계정 한도에 걸린다 |
| 조정 불가 | Delete/Update/Tag/Untag/ListTags | 계정 50 TPS, 리소스당 5 TPS | 일괄 작업은 속도 조절 |
| 조정 불가 | `UpdateMediaStorageConfiguration` | 계정 10 TPS, 리소스당 5 TPS | 저장 설정 일괄 변경 시 속도 조절 |
| 조정 불가 | `GetIceServerConfig` | 채널당 5 TPS | viewer 동시 접속 시 분산 |
| 조정 불가 | TURN 대역폭 / allocation / 자격증명 | 5 Mbps / 채널당 50 / 300초 | 2절 참고 |
| 조정 가능 | viewer 연결 수 | 채널당 10 | 늘려도 디바이스 업링크는 그대로다([16장](/study/webrtc/16-aws-landscape)) |
| 조정 가능 | 시그널링 채널 수(계정·리전) | 문서마다 다르다(아래 참고) | 디바이스 대수 계획에 반영 |
| 조정 가능 | Media Storage Channels(저장 설정 채널) 수 | 100 | 저장 세션을 쓰는 채널 수 계획 |
| 조정 가능 | `CreateSignalingChannel` | 50 TPS | 대량 프로비저닝 속도 |
| 조정 가능 | `GetIceServerConfig` | 계정·리전 100 TPS | 동시 접속 규모 |

::: warning 채널 수 한도는 문서마다 다르다
WebRTC 개발자 가이드의 할당량 표는 시그널링 채널 수를 us-east-1·us-west-2 10,000개, 그 외 리전 5,000개로 적는다. General Reference(Service Quotas 목록)는 us-east-1·us-west-2 20,000개, 그 외 10,000개로 적는다. 둘 다 조정 가능하다. 실제로 적용되는 값은 계정의 Service Quotas 콘솔에서 확인해야 한다.
:::

연결 시간에 관해서는 숫자가 하나 더 있다. `GetIceServerConfig`의 오류 목록에 있는 `SessionExpiredException` 설명은 "클라이언트가 연결된 뒤 세션은 45분간 유효하며, 계속 메시지를 주고받으려면 채널에 다시 연결해야 한다"고 적는다. 할당량 표의 최대 연결 시간 1시간과 숫자가 다르고, 두 수치의 관계를 문서가 설명하지 않는다. 확인이 필요한 부분이므로 재연결 주기는 둘 중 짧은 쪽보다도 여유 있게 잡는 편이 안전하다. 재연결 전략은 [18장](/study/webrtc/18-kvs-signaling-api)에서 구체화한다.

표를 농기계 플랫폼에 대입하면 다음과 같은 설계 항목이 나온다.

- <strong>정전 복구 후 동시 부팅.</strong> 한 농장의 기계 수백 대가 동시에 켜지면 모두가 `GetSignalingChannelEndpoint`를 호출한다. 계정 300 TPS는 조정할 수 없으므로 부팅 후 연결 시작에 무작위 지연(jitter)을 넣고, 실패하면 지수 백오프로 재시도한다.
- <strong>viewer 재접속 폭주.</strong> 관제실 네트워크가 잠깐 끊기면 viewer 여러 명이 같은 채널에 동시에 다시 붙는다. 채널당 3 TPS를 넘으면 `ClientLimitExceededException`이 나므로, 브라우저 쪽 재시도에도 지터를 넣는다.
- <strong>후보 폭주.</strong> 디바이스에 LTE, Wi-Fi, 도커 브리지 같은 인터페이스가 여럿이면 host 후보가 한꺼번에 많이 나온다. `SendIceCandidate`는 연결당 20 TPS이므로 불필요한 인터페이스의 후보를 줄이는 편이 좋다.
- <strong>SDP 크기.</strong> payload 한도 10 KB는 base64 인코딩 후 기준이다. base64는 크기를 약 4/3배로 늘린다. 비디오 트랙과 코덱 목록이 많은 offer는 이 한도를 의식해야 한다.

## 5. KVS Video Streams(Producer SDK)와의 관계

"Kinesis Video Streams"라는 이름 아래에는 기능이 둘 있다. 이 장에서 다룬 <strong>WebRTC</strong>(실시간 P2P)와, 원래부터 있던 <strong>Video Streams</strong>(수집·저장·재생)다. 둘은 같은 서비스 네임스페이스(`kinesisvideo`)를 쓰고 CLI 명령도 `aws kinesisvideo create-signaling-channel`과 `aws kinesisvideo create-stream`처럼 나란히 있어서 자주 혼동된다.

![Kinesis Video Streams의 두 기능. 위쪽 KVS WebRTC는 디바이스(C SDK, Master)와 브라우저(Viewer)가 시그널링 채널·STUN/TURN과 점선으로 연결되고 미디어는 둘 사이에 P2P로 흐른다. 아래쪽 KVS Video Streams는 디바이스(Producer SDK, kvssink)가 PutMedia로 Kinesis Video Stream(프래그먼트, 보존 기간)에 보내고, 스트림은 HLS·DASH 재생, GetMedia, GetImages로 소비된다. 시그널링 채널에서 Kinesis Video Stream으로 내려가는 점선 화살표가 WebRTC 인제스트(저장 세션, UpdateMediaStorageConfiguration·JoinStorageSession)를 나타낸다](/images/study-webrtc/17-kvs-family-light.png)
![Kinesis Video Streams의 두 기능. 위쪽 KVS WebRTC는 디바이스(C SDK, Master)와 브라우저(Viewer)가 시그널링 채널·STUN/TURN과 점선으로 연결되고 미디어는 둘 사이에 P2P로 흐른다. 아래쪽 KVS Video Streams는 디바이스(Producer SDK, kvssink)가 PutMedia로 Kinesis Video Stream(프래그먼트, 보존 기간)에 보내고, 스트림은 HLS·DASH 재생, GetMedia, GetImages로 소비된다. 시그널링 채널에서 Kinesis Video Stream으로 내려가는 점선 화살표가 WebRTC 인제스트(저장 세션, UpdateMediaStorageConfiguration·JoinStorageSession)를 나타낸다](/images/study-webrtc/17-kvs-family-dark.png)

| 항목 | KVS WebRTC | KVS Video Streams |
|---|---|---|
| 핵심 리소스 | 시그널링 채널 | 스트림(Kinesis Video Stream) |
| 목적 | 실시간 양방향 시청·통화·제어 | 영상 수집, 보존 기간 동안 저장, 재생·분석 |
| 미디어 경로 | 피어 간 P2P(필요 시 TURN) | 디바이스 → AWS 스트림 → 소비자 |
| 디바이스 SDK | WebRTC C SDK | Producer SDK(GStreamer `kvssink` 플러그인 포함) |
| 소비 방식 | 브라우저 `RTCPeerConnection` | HLS·DASH 재생, GetMedia, GetClip, GetImages 등 |
| 지연 | 서버 홉 없는 실시간 | HLS·DASH는 세그먼트 기반이라 초 단위 |
| 과금 축 | 채널·메시지·TURN 분(+ relay 데이터 전송) | 데이터 수집량(GB) 등. 참고로 수집 단가는 us-east-1 $0.0085/GB, 서울 $0.0104/GB(2026년 10월 기준) |

두 기능을 잇는 지점이 <strong>WebRTC 인제스트</strong>다. `UpdateMediaStorageConfiguration`으로 시그널링 채널에 스트림을 연결하고 저장을 켜면, 디바이스는 `JoinStorageSession`으로 AWS 쪽 저장 세션에 붙고 저장 세션이 미디어를 스트림에 기록한다. 문서는 이를 "sub 1-second latency 미디어 스트리밍과 클라우드 수집·저장"으로 소개한다. 저장된 미디어는 HLS·DASH 재생, GetImages 같은 Video Streams 기능을 그대로 쓴다.

대신 이 모드에서는 이 장에서 설명한 P2P 구조가 사라진다. 저장을 켜면 master와 viewer의 직접 연결이 더 이상 일어나지 않고, viewer도 저장 세션에 붙는다. 저장 세션은 Amazon 네트워크 안에 있어서 relay 후보만 보내고, Trickle ICE가 필수다. viewer는 최대 3명, 세션은 최대 1시간이며, 문서상 H.264 비디오와 Opus 오디오가 모두 필요하다(C SDK에는 비디오만 보내는 저장 샘플도 있어 문서와 어긋난다).

그래서 "녹화도 하고 실시간으로도 본다"는 요구에는 길이 둘이다. 하나는 WebRTC 인제스트로 한 번만 올리고 저장 세션의 제약을 받아들이는 길이다. 다른 하나는 실시간은 KVS WebRTC P2P로, 녹화는 Producer SDK로 따로 올리는 길이다. 후자는 제약이 적은 대신 디바이스 업링크와 인코딩 부담이 늘어난다. 이 비교와 구현은 [21장](/study/webrtc/21-kvs-ingestion-storage)에서 다룬다.

::: tip 핵심 정리
- 시그널링 채널은 SDP·ICE를 중계하는 관리형 "방"이다. 구조는 master 1 : viewer 기본 10(조정 가능)이고, 채널 타입은 `SINGLE_MASTER`만 지원한다.
- master는 ClientId 없이, viewer는 ClientId(1~256자, `AWS_` 접두사 금지)로 연결한다. 같은 신원으로 다시 연결하면 새 연결이 기존 연결을 대체하고, viewer끼리는 서로 보지 못한다.
- KVS는 STUN·TURN도 운영한다. 모든 엔드포인트가 `*.kinesisvideo.{region}.amazonaws.com`과 443 포트로 수렴한다. TURN 자격증명은 300초, 세션당 5 Mbps, 채널당 allocation 50이며 모두 조정할 수 없다.
- 연결 순서는 GetSignalingChannelEndpoint → GetIceServerConfig → SigV4 서명 WSS 연결 → SDP_OFFER/SDP_ANSWER/ICE_CANDIDATE 중계 → P2P 또는 TURN 미디어다. 디바이스가 ①~③을 미리 끝내 두면 시청 시작이 빨라진다.
- 연결 1시간·idle 10분·GO_AWAY 유예 60초는 조정할 수 없다. 채널 수 한도는 문서마다 다르므로 Service Quotas 콘솔에서 확인한다.
- KVS WebRTC와 Video Streams는 같은 서비스의 다른 기능이고, WebRTC 인제스트가 둘을 잇는다. 이 모드에서는 P2P가 아니라 저장 세션 경유가 된다.
:::

## 다음 챕터

[KVS 시그널링 API 상세](/study/webrtc/18-kvs-signaling-api)에서는 이 장의 연결 순서를 API 수준으로 내려간다. 컨트롤 플레인 API와 AWS CLI 예제, SigV4 서명 WSS URL 구성, 송수신 메시지 JSON 포맷, ClientId 설계, 1시간 연결 한도와 idle timeout에 대응하는 재연결 전략을 다룬다.

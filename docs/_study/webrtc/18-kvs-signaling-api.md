---
title: "KVS 시그널링 API 상세"
description: "KVS WebRTC의 컨트롤 플레인 API와 AWS CLI·SDK 예제, GetSignalingChannelEndpoint·GetIceServerConfig, SigV4 서명 WSS URL의 구성, 송수신 메시지 JSON 포맷, ClientId 설계, 1시간 연결 한도·10분 idle·GO_AWAY에 대응하는 재연결과 오류 처리를 API 수준에서 정리한다."
date: 2026-10-19
tags: [WebRTC, AWS, Kinesis Video Streams, SigV4, Signaling, WebSocket]
prev: /study/webrtc/17-kvs-architecture
next: /study/webrtc/19-kvs-c-sdk
---

# KVS 시그널링 API 상세

::: info 학습 목표
- KVS 시그널링 API가 컨트롤 플레인·채널 HTTPS·채널 WSS 엔드포인트 중 어디로 가는지 구분하고, AWS CLI로 채널 수명주기를 다룰 수 있다.
- GetSignalingChannelEndpoint와 GetIceServerConfig를 CLI와 SDK(Java v2, JavaScript v3)로 호출하고 결과를 `RTCPeerConnection` 설정으로 바꿀 수 있다.
- SigV4 서명 WSS URL이 어떤 쿼리 파라미터와 정규 요청으로 만들어지는지 설명하고, 백엔드가 서명 URL을 발급하는 구조를 구현할 수 있다.
- 송신 메시지(action·recipientClientId·messagePayload·correlationId)와 수신 이벤트(messageType·senderClientId·statusResponse)의 형식과 한도를 안다.
- 유일성과 추적성을 갖춘 ClientId를 설계하고, 1시간 연결 한도·10분 idle·GO_AWAY·오류 상황별 재연결 전략을 세울 수 있다.
:::

## 1. API 지도와 엔드포인트 계층

[17장](/study/webrtc/17-kvs-architecture)의 연결 순서에 등장한 API는 서로 다른 엔드포인트로 간다. 이걸 섞으면 "API를 불렀는데 엔드포인트가 없다"는 오류부터 만난다. 먼저 계층을 나눠 두자.

![KVS 시그널링 API의 엔드포인트 계층. 왼쪽 호출 주체는 백엔드(프로비저닝), 디바이스(Master), 브라우저(Viewer)이고, 오른쪽 계층은 위에서부터 컨트롤 플레인(kinesisvideo.{region}.amazonaws.com: Create/Describe/List/Update/Delete SignalingChannel, Tag·Untag·ListTags·GetSignalingChannelEndpoint), 채널 HTTPS 엔드포인트(r-xxxxxxxx: GetIceServerConfig·SendAlexaOfferToMaster), 채널 WSS 엔드포인트(m-xxxxxxxx: ConnectAsMaster·ConnectAsViewer, SDP_OFFER·SDP_ANSWER·ICE_CANDIDATE), 채널 WEBRTC 엔드포인트(저장 설정 채널만: JoinStorageSession·JoinStorageSessionAsViewer)다. 디바이스와 브라우저는 컨트롤 플레인·HTTPS·WSS를 모두 호출하고, 브라우저의 컨트롤 플레인·HTTPS 호출은 백엔드가 대신해 줄 수 있어 점선으로 표시돼 있다](/images/study-webrtc/18-endpoint-layers-light.png)
![KVS 시그널링 API의 엔드포인트 계층. 왼쪽 호출 주체는 백엔드(프로비저닝), 디바이스(Master), 브라우저(Viewer)이고, 오른쪽 계층은 위에서부터 컨트롤 플레인(kinesisvideo.{region}.amazonaws.com: Create/Describe/List/Update/Delete SignalingChannel, Tag·Untag·ListTags·GetSignalingChannelEndpoint), 채널 HTTPS 엔드포인트(r-xxxxxxxx: GetIceServerConfig·SendAlexaOfferToMaster), 채널 WSS 엔드포인트(m-xxxxxxxx: ConnectAsMaster·ConnectAsViewer, SDP_OFFER·SDP_ANSWER·ICE_CANDIDATE), 채널 WEBRTC 엔드포인트(저장 설정 채널만: JoinStorageSession·JoinStorageSessionAsViewer)다. 디바이스와 브라우저는 컨트롤 플레인·HTTPS·WSS를 모두 호출하고, 브라우저의 컨트롤 플레인·HTTPS 호출은 백엔드가 대신해 줄 수 있어 점선으로 표시돼 있다](/images/study-webrtc/18-endpoint-layers-dark.png)

| 계층 | 서비스(API 버전) | 주요 API | SDK 클라이언트 |
|---|---|---|---|
| 컨트롤 플레인 | `kinesisvideo` (2017-09-30) | `CreateSignalingChannel`, `DescribeSignalingChannel`, `ListSignalingChannels`, `UpdateSignalingChannel`, `DeleteSignalingChannel`, `GetSignalingChannelEndpoint`, `TagResource`, `UntagResource`, `ListTagsForResource`, `UpdateMediaStorageConfiguration`, `DescribeMediaStorageConfiguration`, `DescribeMappedResourceConfiguration` | JS v3 `@aws-sdk/client-kinesis-video`, Java v2 `KinesisVideoClient` |
| 채널 HTTPS 엔드포인트 | `kinesis-video-signaling` (2019-12-04) | `GetIceServerConfig`, `SendAlexaOfferToMaster` | JS v3 `@aws-sdk/client-kinesis-video-signaling`, Java v2 `KinesisVideoSignalingClient` |
| 채널 WSS 엔드포인트 | WebSocket API | `ConnectAsMaster`, `ConnectAsViewer`, `SendSdpOffer`, `SendSdpAnswer`, `SendIceCandidate`, `Disconnect`, 비동기 메시지 수신 | KVS WebRTC SDK(JS `SignalingClient`, C SDK 등) 또는 직접 구현 |
| 채널 WEBRTC 엔드포인트 | webrtc-storage (2018-05-10) | `JoinStorageSession`, `JoinStorageSessionAsViewer` | [21장](/study/webrtc/21-kvs-ingestion-storage) |

채널 HTTPS·WSS·WEBRTC 엔드포인트는 고정 주소가 아니다. 채널과 역할마다 `GetSignalingChannelEndpoint`로 받아야 한다. 그래서 `kinesis-video-signaling` 클라이언트는 기본 엔드포인트로는 쓸 수 없고, 반드시 받은 HTTPS 엔드포인트를 지정해서 만든다.

WSS 계층에는 AWS SDK 클라이언트가 없다. 일반 AWS SDK에는 WebSocket 요청을 서명하는 기능이 없기 때문이다. KVS JS SDK 소스의 `SigV4RequestSigner` 주석도 "AWS SDK는 WebSocket 엔드포인트를 지원하지 않아서 이 용도로 쓸 수 없다"고 적는다. WSS 연결은 KVS WebRTC SDK를 쓰거나, 4절의 서명 규칙대로 직접 URL을 만들어야 한다.

## 2. 채널 수명주기: AWS CLI

농기계 한 대의 채널을 만들고, 확인하고, 바꾸고, 지우는 과정을 CLI로 따라가 보자. 채널 이름은 IoT thing 이름과 같게 둔다([17장](/study/webrtc/17-kvs-architecture)).

```bash
REGION=ap-northeast-2
CHANNEL=tx200-0042          # IoT thing 이름과 동일

# 1) 생성 (비동기)
aws kinesisvideo create-signaling-channel \
  --region "$REGION" \
  --channel-name "$CHANNEL" \
  --channel-type SINGLE_MASTER \
  --single-master-configuration MessageTtlSeconds=60 \
  --tags Key=farm,Value=gimje-01 Key=model,Value=tx200
```

응답에는 `ChannelARN` 하나만 온다. 형식은 다음과 같다(계정 ID와 마지막 숫자는 예시다).

```json
{
  "ChannelARN": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/tx200-0042/1760851200000"
}
```

`CreateSignalingChannel`은 비동기 작업이다. 응답을 받았다고 바로 쓸 수 있는 것이 아니므로 `DescribeSignalingChannel`로 상태가 `ACTIVE`가 될 때까지 기다린다. 이 API는 채널 이름과 ARN 중 하나만 있으면 된다.

```bash
# 2) ACTIVE가 될 때까지 대기 (최대 약 30초)
for i in $(seq 1 15); do
  STATUS=$(aws kinesisvideo describe-signaling-channel \
    --region "$REGION" --channel-name "$CHANNEL" \
    --query 'ChannelInfo.ChannelStatus' --output text)
  echo "status=$STATUS"
  [ "$STATUS" = "ACTIVE" ] && break
  sleep 2
done

CHANNEL_ARN=$(aws kinesisvideo describe-signaling-channel \
  --region "$REGION" --channel-name "$CHANNEL" \
  --query 'ChannelInfo.ChannelARN' --output text)
```

`ChannelInfo`에는 `ChannelARN`, `ChannelName`, `ChannelStatus`(`CREATING | ACTIVE | UPDATING | DELETING`), `ChannelType`, `CreationTime`, `SingleMasterConfiguration`, `Version`이 들어 있다. `Version`은 수정할 때 낙관적 잠금 토큰으로 쓴다.

```bash
# 3) 메시지 TTL 변경: CurrentVersion 필수
VERSION=$(aws kinesisvideo describe-signaling-channel \
  --region "$REGION" --channel-name "$CHANNEL" \
  --query 'ChannelInfo.Version' --output text)

aws kinesisvideo update-signaling-channel \
  --region "$REGION" \
  --channel-arn "$CHANNEL_ARN" \
  --current-version "$VERSION" \
  --single-master-configuration MessageTtlSeconds=30

# 4) 이름 접두사로 목록 조회 (BEGINS_WITH만 지원)
aws kinesisvideo list-signaling-channels \
  --region "$REGION" \
  --channel-name-condition ComparisonOperator=BEGINS_WITH,ComparisonValue=tx200- \
  --query 'ChannelInfoList[].[ChannelName,ChannelStatus]' --output table

# 5) 삭제 (비동기). CurrentVersion을 생략하면 최신 버전을 지운다
aws kinesisvideo delete-signaling-channel \
  --region "$REGION" --channel-arn "$CHANNEL_ARN"
```

`UpdateSignalingChannel`도 비동기이고, `CurrentVersion`이 최신이 아니면 `VersionMismatchException`이 난다. TTL을 바꾸면 변경 이후에 보낸 새 메시지에만 적용된다. `ListSignalingChannels`의 `ChannelNameCondition`은 현재 `BEGINS_WITH`만 지원하므로, 채널 이름에 모델명이나 농장 코드 같은 접두사를 두면 운영 조회가 편하다. `MaxResults`는 1~10,000이고 기본 500이다.

같은 작업을 백엔드 프로비저닝 코드로 옮기면 다음과 같다. 디바이스 등록 시 채널을 만드는 전체 설계는 [20장](/study/webrtc/20-kvs-viewer-backend)에서 다룬다.

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kinesisvideo.KinesisVideoClient;
import software.amazon.awssdk.services.kinesisvideo.model.ChannelInfo;
import software.amazon.awssdk.services.kinesisvideo.model.ChannelType;
import software.amazon.awssdk.services.kinesisvideo.model.Tag;

public class SignalingChannelProvisioner {

    private final KinesisVideoClient kvs = KinesisVideoClient.builder()
            .region(Region.AP_NORTHEAST_2)
            .build();

    /** 채널을 만들고 ACTIVE가 될 때까지 기다린 뒤 ARN을 돌려준다. */
    public String createChannel(String thingName, String farmId) throws InterruptedException {
        String arn = kvs.createSignalingChannel(r -> r
                .channelName(thingName)
                .channelType(ChannelType.SINGLE_MASTER)
                .singleMasterConfiguration(c -> c.messageTtlSeconds(60))
                .tags(Tag.builder().key("farm").value(farmId).build()))
            .channelARN();

        for (int i = 0; i < 30; i++) {
            ChannelInfo info = kvs.describeSignalingChannel(r -> r.channelARN(arn)).channelInfo();
            if ("ACTIVE".equals(info.channelStatusAsString())) {
                return arn;
            }
            Thread.sleep(1_000);
        }
        throw new IllegalStateException("channel not ACTIVE in time: " + arn);
    }
}
```

`CreateSignalingChannel`은 계정 기준 50 TPS(조정 가능), Delete·Update·Tag 계열은 계정 50 TPS·리소스당 5 TPS(조정 불가)다. 수천 대를 한꺼번에 등록하는 배치라면 호출 속도를 이 한도 아래로 묶어야 한다.

## 3. 엔드포인트와 ICE 서버 조회

연결 직전에 필요한 두 가지, 즉 엔드포인트와 ICE 서버를 받는 방법이다.

### CLI로 확인하기

```bash
# 1) 엔드포인트: Protocols는 WSS·HTTPS(·WEBRTC), Role은 MASTER 또는 VIEWER
aws kinesisvideo get-signaling-channel-endpoint \
  --region "$REGION" \
  --channel-arn "$CHANNEL_ARN" \
  --single-master-channel-endpoint-configuration Protocols=WSS,HTTPS,Role=MASTER
```

응답은 프로토콜별 엔드포인트 목록이다. 아래 호스트는 형태를 보여 주는 예시다.

```json
{
  "ResourceEndpointList": [
    { "Protocol": "WSS",   "ResourceEndpoint": "wss://m-xxxxxxxx.kinesisvideo.ap-northeast-2.amazonaws.com" },
    { "Protocol": "HTTPS", "ResourceEndpoint": "https://r-xxxxxxxx.kinesisvideo.ap-northeast-2.amazonaws.com" }
  ]
}
```

`Protocols`에 `WEBRTC`를 넣으면 저장 세션용 엔드포인트를 받는다. 저장(ingestion)이 설정되지 않은 채널에 요청하면 `InvalidArgumentException`이 난다. `Role`은 `MASTER`면 채널의 모든 viewer와 통신하는 엔드포인트를, `VIEWER`면 master하고만 통신하는 엔드포인트를 준다.

```bash
# 2) ICE 서버: 위에서 받은 HTTPS 엔드포인트를 --endpoint-url로 지정
aws kinesis-video-signaling get-ice-server-config \
  --region "$REGION" \
  --endpoint-url "https://r-xxxxxxxx.kinesisvideo.ap-northeast-2.amazonaws.com" \
  --channel-arn "$CHANNEL_ARN" \
  --client-id op-1042-a7f3c9e2 \
  --service TURN
```

요청 필드는 `ChannelARN`(필수), `ClientId`, `Service`(유효값 `TURN`만), `Username`이다. 응답은 `IceServerList[]`이고 항목마다 `Uris[]`, `Username`, `Password`, `Ttl`이 있다. `Ttl`은 300초 고정이다. CLI 레퍼런스는 Ttl 범위를 30~86400으로 적어 API Reference와 다르지만, 실제 운영 기준은 300초로 잡는다([17장](/study/webrtc/17-kvs-architecture)). `Uris`의 정확한 모양(예: `?transport=` 쿼리 포함 여부)은 공식 문서 예시로 확인하지 못했으므로, 직접 호출해서 응답을 보고 확정하는 것이 좋다.

STUN은 이 API로 받지 않는다. 다음 문자열을 직접 넣는다.

```text
stun:stun.kinesisvideo.{region}.amazonaws.com:443      # legacy IPv4 엔드포인트 모드
stun:stun.kinesisvideo.{region}.api.aws:443            # dual-stack 엔드포인트 모드(JS SDK README)
```

### SDK로 호출하기

백엔드 코드에서는 두 호출을 묶어 "엔드포인트 + `iceServers`"를 한 번에 만드는 함수로 둔다.

::: tabs

@tab Java (SDK v2)

```java
import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kinesisvideo.KinesisVideoClient;
import software.amazon.awssdk.services.kinesisvideo.model.ChannelProtocol;
import software.amazon.awssdk.services.kinesisvideo.model.ChannelRole;
import software.amazon.awssdk.services.kinesisvideo.model.ResourceEndpointListItem;
import software.amazon.awssdk.services.kinesisvideosignaling.KinesisVideoSignalingClient;
import software.amazon.awssdk.services.kinesisvideosignaling.model.IceServer;
import software.amazon.awssdk.services.kinesisvideosignaling.model.Service;

public class ViewerConnectionInfoService {

    public record IceServerDto(List<String> urls, String username, String credential) {}
    public record ConnectionInfo(String wssEndpoint, List<IceServerDto> iceServers) {}

    private static final Region REGION = Region.AP_NORTHEAST_2;
    private final KinesisVideoClient kvs = KinesisVideoClient.builder().region(REGION).build();

    public ConnectionInfo resolve(String channelArn, String clientId) {
        // 1) 역할별 엔드포인트
        Map<ChannelProtocol, String> endpoints = kvs.getSignalingChannelEndpoint(r -> r
                .channelARN(channelArn)
                .singleMasterChannelEndpointConfiguration(c -> c
                    .protocols(ChannelProtocol.WSS, ChannelProtocol.HTTPS)
                    .role(ChannelRole.VIEWER)))
            .resourceEndpointList().stream()
            .collect(Collectors.toMap(ResourceEndpointListItem::protocol,
                                      ResourceEndpointListItem::resourceEndpoint));

        // 2) STUN은 문자열, TURN은 채널 HTTPS 엔드포인트로 조회
        List<IceServerDto> iceServers = new ArrayList<>();
        iceServers.add(new IceServerDto(
            List.of("stun:stun.kinesisvideo." + REGION.id() + ".amazonaws.com:443"), null, null));

        try (KinesisVideoSignalingClient signaling = KinesisVideoSignalingClient.builder()
                .region(REGION)
                .endpointOverride(URI.create(endpoints.get(ChannelProtocol.HTTPS)))
                .build()) {
            for (IceServer s : signaling.getIceServerConfig(r -> r
                    .channelARN(channelArn)
                    .clientId(clientId)
                    .service(Service.TURN)).iceServerList()) {
                iceServers.add(new IceServerDto(s.uris(), s.username(), s.password()));
            }
        }
        return new ConnectionInfo(endpoints.get(ChannelProtocol.WSS), iceServers);
    }
}
```

@tab JavaScript (SDK v3)

```js
const { KinesisVideoClient, GetSignalingChannelEndpointCommand } = require('@aws-sdk/client-kinesis-video');
const { KinesisVideoSignalingClient, GetIceServerConfigCommand } = require('@aws-sdk/client-kinesis-video-signaling');

const REGION = 'ap-northeast-2';
const kvs = new KinesisVideoClient({ region: REGION });

async function resolveConnectionInfo(channelARN, role, clientId) {
  // 1) 역할별 엔드포인트
  const { ResourceEndpointList } = await kvs.send(new GetSignalingChannelEndpointCommand({
    ChannelARN: channelARN,
    SingleMasterChannelEndpointConfiguration: { Protocols: ['WSS', 'HTTPS'], Role: role },
  }));
  const endpoints = Object.fromEntries(ResourceEndpointList.map((e) => [e.Protocol, e.ResourceEndpoint]));

  // 2) STUN은 문자열, TURN은 채널 HTTPS 엔드포인트로 조회
  const signaling = new KinesisVideoSignalingClient({ region: REGION, endpoint: endpoints.HTTPS });
  const { IceServerList } = await signaling.send(new GetIceServerConfigCommand({
    ChannelARN: channelARN,
    ClientId: clientId,
    Service: 'TURN',
  }));

  const iceServers = [
    { urls: `stun:stun.kinesisvideo.${REGION}.amazonaws.com:443` },
    ...IceServerList.map((s) => ({ urls: s.Uris, username: s.Username, credential: s.Password })),
  ];
  return { wssEndpoint: endpoints.WSS, iceServers };
}

module.exports = { resolveConnectionInfo };
```

:::

두 호출에는 서로 다른 한도가 걸린다. `GetSignalingChannelEndpoint`는 계정 300 TPS·채널당 5 TPS(조정 불가)이고, `GetIceServerConfig`는 채널당 5 TPS(조정 불가)·계정 100 TPS(조정 가능)다. TURN 자격증명은 300초짜리라 캐시하면 안 되지만, 엔드포인트 호출은 부팅 폭주 때 계정 한도에 걸릴 수 있으므로 짧게 캐시하고 연결이 실패하면 다시 조회하는 방식이 실용적이다. 엔드포인트가 얼마 동안 유효한지는 문서가 명시하지 않는다.

## 4. SigV4 서명 WSS URL

브라우저의 `WebSocket` API는 연결 요청에 임의 헤더를 넣을 수 없다. 그래서 KVS는 WSS 연결을 <strong>쿼리 문자열 방식의 SigV4 서명(presigned URL)</strong>으로 인증한다. 서명이 담긴 URL만 있으면 누구든 그 연결을 열 수 있으므로, URL은 짧게 살아야 하고 서명 대상에 무엇이 들어가는지 알아야 한다.

### URL 구성

KVS JS SDK의 `SigV4RequestSigner` 구현을 기준으로 쿼리 파라미터를 정리하면 다음과 같다.

| 파라미터 | 값 | 비고 |
|---|---|---|
| `X-Amz-ChannelARN` | 채널 ARN | master·viewer 공통, 필수 |
| `X-Amz-ClientId` | viewer ClientId | viewer만, 필수 |
| `X-Amz-Algorithm` | `AWS4-HMAC-SHA256` | |
| `X-Amz-Credential` | `{AccessKeyId}/{yyyymmdd}/{region}/kinesisvideo/aws4_request` | 서명 서비스 이름은 `kinesisvideo` |
| `X-Amz-Date` | `yyyymmddThhmmssZ` (UTC) | |
| `X-Amz-Expires` | `299` | JS SDK 고정값. 만료를 바꾸는 옵션은 없다 |
| `X-Amz-SignedHeaders` | `host` | 서명하는 헤더는 host 하나 |
| `X-Amz-Security-Token` | 세션 토큰 | 임시 자격증명일 때. KVS는 이 값을 <strong>정규 요청에 포함해 서명</strong>해야 한다 |
| `X-Amz-Signature` | 16진 서명 | 위 파라미터로 서명을 계산한 뒤 마지막에 붙인다 |

`X-Amz-Security-Token` 처리는 서비스마다 다르다. AWS 문서는 일부 서비스는 세션 토큰을 서명 대상에 넣어야 하고 다른 서비스는 서명 뒤에 덧붙인다고 설명하는데, JS SDK 소스 주석은 "KVS Signaling Service는 세션 토큰을 정규 요청에 포함해야 한다"고 적는다. 직접 서명기를 만들 때 가장 자주 틀리는 부분이다.

정규 요청(canonical request)과 서명 문자열은 표준 SigV4 형식을 따른다.

```text
# 정규 요청: 메서드, 경로, 정렬·인코딩한 쿼리(X-Amz-Signature 제외), 헤더, 서명 헤더 목록, 페이로드 해시
GET
/
X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-ChannelARN=arn%3Aaws%3Akinesisvideo%3A...&X-Amz-ClientId=op-1042-a7f3c9e2&X-Amz-Credential=...&X-Amz-Date=20261019T030000Z&X-Amz-Expires=299&X-Amz-Security-Token=...&X-Amz-SignedHeaders=host
host:m-xxxxxxxx.kinesisvideo.ap-northeast-2.amazonaws.com

host
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855   # 빈 문자열의 SHA-256

# 서명 문자열
AWS4-HMAC-SHA256
20261019T030000Z
20261019/ap-northeast-2/kinesisvideo/aws4_request
<정규 요청의 SHA-256 16진값>

# 서명 키: HMAC 체인
kDate    = HMAC("AWS4" + SecretAccessKey, "20261019")
kRegion  = HMAC(kDate, "ap-northeast-2")
kService = HMAC(kRegion, "kinesisvideo")
kSigning = HMAC(kService, "aws4_request")
X-Amz-Signature = hex(HMAC(kSigning, 서명 문자열))
```

최종 URL은 `wss://{호스트}/?{쿼리}&X-Amz-Signature={서명}` 모양이 된다. 메서드는 항상 `GET`이고, 엔드포인트에 경로가 없으면 경로는 `/`다.

### 시간과 만료

서명에는 시각이 들어간다. JS SDK README는 `getSignedURL`의 `date` 인자를 "서명이 유효한 시각(±5분)"으로 설명한다. 디바이스 시계가 5분 넘게 틀어지면 서명이 거부된다. RTC 배터리가 없는 임베디드 보드는 부팅 직후 NTP 동기화를 끝낸 뒤에 연결해야 하고([13장](/study/webrtc/13-native-webrtc)), 브라우저 쪽은 JS SDK의 `systemClockOffset` 옵션으로 서버 시각과의 차이를 보정할 수 있다.

`X-Amz-Expires=299`는 URL로 연결을 여는 데 쓸 수 있는 시간 창이다. 연결이 맺어진 뒤 얼마나 유지되는지는 이 값이 아니라 [17장](/study/webrtc/17-kvs-architecture)의 최대 연결 시간(1시간)이 정한다. 따라서 <strong>재연결할 때마다 새로 서명한 URL</strong>을 써야 하고, 서명에 쓴 자격증명이 만료됐다면 자격증명부터 갱신해야 한다.

### 백엔드가 서명 URL을 발급하는 구조

브라우저에 AWS 자격증명을 두지 않으려면, 백엔드가 엔드포인트·ICE 서버 조회와 서명을 모두 하고 결과만 넘겨주면 된다. JS SDK README도 이 방식을 안내하며, Node.js 백엔드에서는 SDK의 `SigV4RequestSigner`를 그대로 쓸 수 있다고 적는다. ICE 서버 설정도 백엔드에서 받아 함께 넘겨줘야 한다.

![백엔드가 SigV4 서명 URL을 발급하는 뷰어 접속 흐름. 운영자 브라우저가 앱 로그인 토큰으로 백엔드에 POST /viewer-sessions를 보내면, 백엔드는 운영자와 기계 사이의 권한을 확인한 뒤 KVS API·채널 HTTPS에 GetSignalingChannelEndpoint(VIEWER)와 GetIceServerConfig를 호출해 WSS 엔드포인트와 TURN 자격증명을 받는다. 백엔드는 ClientId를 만들고 X-Amz-Expires 299초로 SigV4 서명을 한 뒤 signedUrl, iceServers, clientId를 브라우저에 돌려준다. 브라우저는 서명 URL 그대로 채널 WSS 엔드포인트에 WebSocket 연결을 열고 101 Switching Protocols를 받은 뒤 시그널링을 시작한다. 브라우저에는 AWS 자격증명이 없다](/images/study-webrtc/18-presign-flow-light.png)
![백엔드가 SigV4 서명 URL을 발급하는 뷰어 접속 흐름. 운영자 브라우저가 앱 로그인 토큰으로 백엔드에 POST /viewer-sessions를 보내면, 백엔드는 운영자와 기계 사이의 권한을 확인한 뒤 KVS API·채널 HTTPS에 GetSignalingChannelEndpoint(VIEWER)와 GetIceServerConfig를 호출해 WSS 엔드포인트와 TURN 자격증명을 받는다. 백엔드는 ClientId를 만들고 X-Amz-Expires 299초로 SigV4 서명을 한 뒤 signedUrl, iceServers, clientId를 브라우저에 돌려준다. 브라우저는 서명 URL 그대로 채널 WSS 엔드포인트에 WebSocket 연결을 열고 101 Switching Protocols를 받은 뒤 시그널링을 시작한다. 브라우저에는 AWS 자격증명이 없다](/images/study-webrtc/18-presign-flow-dark.png)

```js
// server.js — Node.js 18+, CommonJS
const crypto = require('node:crypto');
const express = require('express');
const { fromNodeProviderChain } = require('@aws-sdk/credential-providers');
const { SigV4RequestSigner } = require('amazon-kinesis-video-streams-webrtc');
const { resolveConnectionInfo } = require('./kvs-connection-info'); // 3절의 함수

const REGION = 'ap-northeast-2';
const credentialsProvider = fromNodeProviderChain();
const sessions = new Map(); // clientId → { operatorId, machineId, channelARN, wssEndpoint }  (예시용 메모리 저장소)

async function signViewerUrl({ wssEndpoint, channelARN, clientId }) {
  const { accessKeyId, secretAccessKey, sessionToken } = await credentialsProvider();
  const signer = new SigV4RequestSigner(REGION, { accessKeyId, secretAccessKey, sessionToken });
  return signer.getSignedURL(wssEndpoint, {
    'X-Amz-ChannelARN': channelARN,
    'X-Amz-ClientId': clientId,
  });
}

const app = express();

// 시청 세션 생성: 엔드포인트·ICE 서버·서명 URL을 한 번에 돌려준다
app.post('/api/machines/:machineId/viewer-sessions', requireOperator, async (req, res) => {
  const { machineId } = req.params;
  const operatorId = req.operator.id;                  // 앱 인증 미들웨어가 채운 값
  if (!(await canView(operatorId, machineId))) return res.sendStatus(403);

  const channelARN = await findChannelArn(machineId);  // 기계 ↔ 채널 ARN 매핑(DB)
  const clientId = `op-${operatorId}-${crypto.randomBytes(4).toString('hex')}`;
  const { wssEndpoint, iceServers } = await resolveConnectionInfo(channelARN, 'VIEWER', clientId);

  sessions.set(clientId, { operatorId, machineId, channelARN, wssEndpoint });
  const signedUrl = await signViewerUrl({ wssEndpoint, channelARN, clientId });
  res.json({ region: REGION, channelARN, clientId, wssEndpoint, signedUrl, iceServers });
});

// 재연결용 재서명: 같은 ClientId로 새 URL만 발급한다
app.post('/api/viewer-sessions/:clientId/signed-url', requireOperator, async (req, res) => {
  const s = sessions.get(req.params.clientId);
  if (!s || s.operatorId !== req.operator.id) return res.sendStatus(404);
  if (!(await canView(s.operatorId, s.machineId))) return res.sendStatus(403); // 권한 회수 반영
  res.json({ signedUrl: await signViewerUrl({ ...s, clientId: req.params.clientId }) });
});
```

`requireOperator`, `canView`, `findChannelArn`은 앱의 인증·권한·DB 계층이다. 이 구조에서 주의할 점이 셋 있다.

- <strong>서명에 쓰는 자격증명의 권한이 곧 브라우저의 권한이다.</strong> 서명 URL로 열린 연결은 백엔드 IAM 주체의 권한으로 인가된다. 백엔드 역할에는 `kinesisvideo:ConnectAsViewer`가 필요하고, 그 권한이 모든 채널에 열려 있으면 버그 하나로 다른 기계의 영상이 열린다. 요청마다 STS `AssumeRole`에 세션 정책을 붙여 해당 채널 ARN으로만 좁힌 임시 자격증명으로 서명하는 방법이 안전하다. 이 패턴은 [20장](/study/webrtc/20-kvs-viewer-backend)에서 구현한다.
- <strong>ClientId가 서명에 묶인다.</strong> `X-Amz-ClientId`는 서명 대상 쿼리에 들어가므로 브라우저가 바꾸면 서명이 깨진다. 백엔드가 ClientId를 정하면 master 쪽에서 받은 `senderClientId`를 "백엔드가 인증한 운영자"로 믿을 수 있다.
- <strong>재서명 경로에서도 권한을 다시 확인한다.</strong> 시청 도중 권한이 회수됐다면 다음 재연결에서 막혀야 한다.

브라우저는 JS SDK의 `SignalingClient`에 자격증명 대신 `requestSigner`를 넘긴다. `SignalingClient`는 연결을 열 때마다 `getSignedURL`을 호출하므로, 여기서 백엔드 재서명 API를 부르면 된다.

```js
// 브라우저 — window.KVSWebRTC (amazon-kinesis-video-streams-webrtc)
const session = await fetch(`/api/machines/${machineId}/viewer-sessions`, {
  method: 'POST', credentials: 'include',
}).then((r) => r.json());

let firstUrl = session.signedUrl;   // 첫 연결은 이미 받은 URL을 쓴다
const requestSigner = {
  async getSignedURL() {
    if (firstUrl) { const u = firstUrl; firstUrl = null; return u; }
    const r = await fetch(`/api/viewer-sessions/${session.clientId}/signed-url`, {
      method: 'POST', credentials: 'include',
    });
    if (!r.ok) throw new Error(`resign failed: ${r.status}`);
    return (await r.json()).signedUrl;
  },
};

const pc = new RTCPeerConnection({ iceServers: session.iceServers });
const signalingClient = new KVSWebRTC.SignalingClient({
  channelARN: session.channelARN,
  channelEndpoint: session.wssEndpoint,
  clientId: session.clientId,
  role: KVSWebRTC.Role.VIEWER,
  region: session.region,
  requestSigner,
});
```

## 5. 메시지 포맷

WSS 연결이 열리면 양쪽은 JSON 텍스트 프레임을 주고받는다. 보내는 형식과 받는 형식이 다르다.

### 송신: action·recipientClientId·messagePayload·correlationId

```json
{
  "action": "SDP_ANSWER",
  "recipientClientId": "op-1042-a7f3c9e2",
  "messagePayload": "eyJ0eXBlIjoiYW5zd2VyIiwic2RwIjoidj0wXHJcbm89LSA0NjExNzMxNDAwNDMwMDUxMzM2IDIgSU4gSVA0IDEyNy4wLjAuMVxyXG4uLi4ifQ==",
  "correlationId": "ans-1760851200123"
}
```

| 필드 | 제약 | 설명 |
|---|---|---|
| `action` | `SDP_OFFER`, `SDP_ANSWER`, `ICE_CANDIDATE` | 필수 |
| `recipientClientId` | 1~256자, `[a-zA-Z0-9_.-]+` | master가 보낼 때 필수. viewer가 보내면 무시되고 항상 master로 간다. 스키마 표기는 `SendSdpOffer`에서 Required: Yes, `SendIceCandidate`에서 Required: No로 다르다 |
| `messagePayload` | base64, 최대 10K | 필수. 아래 내용물 참고 |
| `correlationId` | 1~256자, `[a-zA-Z0-9_.-]+` | 선택. 성공하면 응답이 없고, 실패했을 때 이 값을 넣었다면 오류가 `STATUS_RESPONSE`로 돌아온다 |

### 수신: messageType·senderClientId·statusResponse

```json
{
  "senderClientId": "op-1042-a7f3c9e2",
  "messageType": "ICE_CANDIDATE",
  "messagePayload": "eyJjYW5kaWRhdGUiOiJjYW5kaWRhdGU6MSAxIHVkcCAyMTIyMjYwMjIzIDE5Mi4xNjguMC4xMCA1MDAwMCB0eXAgaG9zdCIsInNkcE1pZCI6IjAiLCJzZHBNTGluZUluZGV4IjowfQ=="
}
```

| 필드 | 제약 | 설명 |
|---|---|---|
| `messageType` | `SDP_OFFER`, `SDP_ANSWER`, `ICE_CANDIDATE`, `GO_AWAY`, `RECONNECT_ICE_SERVER`, `STATUS_RESPONSE` | 필수 |
| `senderClientId` | 1~256자, `[a-zA-Z0-9_.-]+` | 선택. master가 viewer 메시지를 받을 때 누가 보냈는지 알려 준다 |
| `messagePayload` | base64, 최대 10K | 선택. `STATUS_RESPONSE`나 서비스 신호에는 없을 수 있다 |
| `statusResponse.correlationId` | 1~256자 | 실패한 원래 메시지의 correlationId |
| `statusResponse.errorType` | 1~256자 | 오류 이름 |
| `statusResponse.statusCode` | 1~256자 | 오류 성격에 대응하는 HTTP 상태 코드(문자열) |
| `statusResponse.description` | 최대 1K | 설명 |

### messagePayload의 내용물

문서는 `messagePayload`를 "base64 인코딩된 메시지 내용"으로만 정의한다. 내용물 형식은 JS SDK 소스 기준으로 `RTCSessionDescription`이나 `RTCIceCandidate`를 `JSON.stringify`한 문자열이다. C SDK와 JS SDK가 서로 통신하므로 사실상의 규약으로 보면 된다. 위 두 예시를 디코딩하면 다음과 같다.

```json
{"type":"answer","sdp":"v=0\r\no=- 4611731400430051336 2 IN IP4 127.0.0.1\r\n..."}
{"candidate":"candidate:1 1 udp 2122260223 192.168.0.10 50000 typ host","sdpMid":"0","sdpMLineIndex":0}
```

base64는 크기를 약 4/3배로 늘리므로 10K 한도는 원본 SDP 기준으로 더 빡빡하다. 트랙과 코덱 목록이 많은 offer를 만들 때 의식해야 한다.

### SDK 없이 직접 다루기

메시지 규약이 단순해서 테스트용 도구나 지원되지 않는 언어에서는 직접 구현할 수도 있다. 아래는 Node.js `ws` 라이브러리로 master 쪽 메시지를 처리하는 골격이다. `onOffer`, `onRemoteCandidate`는 미디어 스택에 연결하는 부분이다.

```js
const WebSocket = require('ws');

const enc = (obj) => Buffer.from(JSON.stringify(obj)).toString('base64');
const dec = (b64) => JSON.parse(Buffer.from(b64, 'base64').toString('utf8'));

function connectMaster(signedMasterUrl, { onOffer, onRemoteCandidate, onGoAway, onReconnectIce }) {
  const ws = new WebSocket(signedMasterUrl);

  // 핸드셰이크가 101이 아니면 상태 코드를 볼 수 있다 (403·404·400 등)
  ws.on('unexpected-response', (_req, res) => console.error('[kvs] handshake failed', res.statusCode));

  ws.on('message', async (raw) => {
    const msg = JSON.parse(raw.toString());
    switch (msg.messageType) {
      case 'SDP_OFFER': {
        const offer = dec(msg.messagePayload);               // { type: 'offer', sdp }
        const answerSdp = await onOffer(msg.senderClientId, offer);
        ws.send(JSON.stringify({
          action: 'SDP_ANSWER',
          recipientClientId: msg.senderClientId,             // master는 수신자 지정 필수
          messagePayload: enc({ type: 'answer', sdp: answerSdp }),
          correlationId: `ans-${Date.now()}`,
        }));
        break;
      }
      case 'ICE_CANDIDATE':
        onRemoteCandidate(msg.senderClientId, dec(msg.messagePayload));
        break;
      case 'STATUS_RESPONSE':
        console.warn('[kvs] delivery failed', msg.statusResponse);
        break;
      case 'GO_AWAY':
        onGoAway();                                          // 60초 안에 재연결
        break;
      case 'RECONNECT_ICE_SERVER':
        onReconnectIce();                                    // ICE 설정 재조회
        break;
      default:
        break;                                               // 모르는 타입은 무시(전방 호환)
    }
  });
  return ws;
}
```

메시지 송신에는 연결당 한도가 있다. `SendSdpOffer`·`SendSdpAnswer`는 WebSocket 연결당 5 TPS, `SendIceCandidate`는 20 TPS다. 송신 API는 멱등이 아니고, 같은 내용을 다시 보내면 새 메시지로 처리된다. 운영 환경에서는 모든 메시지에 `correlationId`를 넣는 것을 권한다. 넣지 않으면 실패해도 아무 신호가 없어서, "offer는 보냈는데 answer가 안 온다"는 증상만 남는다.

## 6. ClientId 설계

ClientId는 문자열 하나지만 동작에 미치는 영향이 크다. 핵심 규칙은 <strong>같은 ClientId로 새 연결이 들어오면 기존 연결을 대체한다</strong>는 것이다. 여기서 설계 요구가 나온다.

| 요구 | 이유 | 방법 |
|---|---|---|
| 동시에 열린 연결마다 유일 | 운영자가 탭 두 개로 같은 기계를 열면, ClientId가 같을 때 두 번째 탭이 첫 번째 연결을 밀어낸다 | 운영자 ID에 세션별 난수를 붙인다 |
| 재연결 시에는 그대로 유지 | 새 ClientId로 다시 붙으면 이전 연결이 끊긴 것을 서비스가 알기 전까지 viewer 자리를 이중으로 차지할 수 있다. 같은 ClientId면 기존 연결이 대체된다 | 시청 세션 동안 ClientId를 고정하고 재서명만 한다 |
| 패턴 준수 | `[a-zA-Z0-9_.-]`, 1~256자, `AWS_` 접두사 금지(대소문자 무시) | 이메일·한글·콜론·슬래시를 쓰지 않는다 |
| 추적 가능 | master 로그와 장애 분석에서 누가 붙었는지 알아야 한다 | 내부 운영자 ID를 넣는다 |
| 개인정보 최소화 | ClientId는 디바이스와 로그에 그대로 남는다 | 이름·이메일 대신 숫자 ID를 쓴다 |
| 신뢰 가능 | master가 `senderClientId`로 권한을 판단하려면 위조할 수 없어야 한다 | 백엔드가 ClientId를 정하고 서명한다(4절) |

이 조건을 만족하는 형식의 예는 `op-{운영자ID}-{세션 난수}`다.

| ClientId | 판정 | 이유 |
|---|---|---|
| `op-1042-a7f3c9e2` | 적합 | 운영자 1042의 한 시청 세션 |
| `svc-recorder-01` | 적합 | 사람이 아닌 서비스 viewer는 접두사로 구분 |
| `operator-1042` | 주의 | 같은 운영자의 두 번째 탭이 첫 번째 연결을 밀어낸다 |
| `kim@agmo.farm` | 부적합 | `@`는 패턴 밖이고 개인정보다 |
| `op:1042` | 부적합 | `:`는 패턴 밖이다 |
| `AWS_viewer1` | 부적합 | `AWS_` 접두사는 금지다 |

master 쪽 구현은 ClientId를 PeerConnection 맵의 키로 쓴다. 같은 ClientId에서 새 `SDP_OFFER`가 오면 이전 PeerConnection을 닫고 새로 만드는 것이 기본이다. viewer가 새로고침했거나 ICE restart를 위해 다시 협상하는 경우다. master는 동시에 PeerConnection을 여러 개 유지하므로, 맵 크기에 상한을 두고 오래된 연결을 정리하는 로직도 필요하다. 이 부분은 [19장](/study/webrtc/19-kvs-c-sdk)의 C SDK 샘플 구조에서 다시 본다.

## 7. 재연결·idle·오류 처리

시그널링 연결은 언젠가 반드시 끊긴다. KVS에는 조정할 수 없는 연결 수명 규칙이 셋 있다. 최대 연결 시간 1시간, 최대 idle timeout 10분, 그리고 `GO_AWAY` 이후 유예 1분이다. 장시간 동작하는 디바이스라면 재연결은 예외 처리가 아니라 정상 흐름이다.

![시그널링 연결 수명 타임라인(0~65분). 대응 없음 행에서는 WS 연결이 60분 지점의 "연결 상한 3,600초" 선에서 서버에 의해 종료된다. 사전 재연결 행에서는 WS #1이 40분 무렵까지 유지되고, 40분±지터에 새 URL로 WS #2를 먼저 연결한 뒤 WS #1을 닫는다. GO_AWAY 수신 행에서는 22분 무렵 GO_AWAY를 받고 60초 유예 안에 새 WS로 갈아타며, 새 WS가 40분부터 메시지 없이 10분을 보내면 50분에 idle로 종료된다](/images/study-webrtc/18-reconnect-timeline-light.png)
![시그널링 연결 수명 타임라인(0~65분). 대응 없음 행에서는 WS 연결이 60분 지점의 "연결 상한 3,600초" 선에서 서버에 의해 종료된다. 사전 재연결 행에서는 WS #1이 40분 무렵까지 유지되고, 40분±지터에 새 URL로 WS #2를 먼저 연결한 뒤 WS #1을 닫는다. GO_AWAY 수신 행에서는 22분 무렵 GO_AWAY를 받고 60초 유예 안에 새 WS로 갈아타며, 새 WS가 40분부터 메시지 없이 10분을 보내면 50분에 idle로 종료된다](/images/study-webrtc/18-reconnect-timeline-dark.png)

### 상황별 전략

<strong>1시간 상한: 사전 재연결.</strong> 끊기기를 기다리지 말고 미리 갈아탄다. `GetIceServerConfig`의 `SessionExpiredException` 설명에는 "연결 후 45분"이라는 별도 수치도 있으므로([17장](/study/webrtc/17-kvs-architecture)), 이 스터디는 40분에 무작위 지터를 더한 시점을 권장값으로 쓴다. 지터는 같은 시각에 부팅한 디바이스들이 같은 시각에 재연결하는 것을 막는다. 순서는 make-before-break다. 새로 서명한 URL로 새 연결을 먼저 열고, 열리면 이전 연결을 닫는다. 같은 신원(master, 또는 같은 ClientId의 viewer)이므로 서비스 쪽에서는 새 연결이 기존 연결을 대체한다.

<strong>idle 10분: 역할에 따라 다르게.</strong> 문서는 idle의 정의(어떤 트래픽이 활동으로 치는지)를 밝히지 않는다. C SDK는 시그널링 WebSocket에 10초 간격으로 ping/pong을 보내도록 구현돼 있다. 반면 브라우저의 `WebSocket` API에는 ping 프레임을 보내는 기능이 없다. 그래서 정책을 역할별로 나눈다.

| 역할 | 정책 | 이유 |
|---|---|---|
| master(디바이스) | 항상 연결 유지. ping으로 활동 유지, 40분 무렵 사전 재연결 | 언제든 새 viewer의 offer를 받아야 한다 |
| viewer(브라우저), 협상 중 | 연결 유지. 끊기면 즉시 재연결 | SDP·ICE 교환이 끝나지 않았다 |
| viewer, 미디어 연결 후 | 끊겨도 바로 다시 붙지 않는다. ICE가 `disconnected`·`failed`가 되거나 재협상이 필요할 때 다시 연결한다 | 미디어 수립 후에는 시그널링이 필요 없고, 10분마다 재연결하는 것은 낭비다 |

<strong>GO_AWAY: 60초 안에 재연결.</strong> 배포나 점검 때 서비스가 보내는 신호다. 문서는 이전 메시지를 처리한 뒤 연결을 끊고 다시 붙으라고 안내한다. 유예는 1분(조정 불가)이다.

<strong>RECONNECT_ICE_SERVER: TURN 경로 교체.</strong> relay 연결을 닫겠다는 신호다. 새 ICE 서버 설정을 받아 다시 연결하라는 뜻이므로, `GetIceServerConfig`를 다시 호출하고 PeerConnection에 반영한 뒤 ICE restart를 한다. 브라우저에서는 `pc.setConfiguration({ iceServers })` 후 `pc.restartIce()`로 재협상을 일으킨다([06장](/study/webrtc/06-ice)).

::: warning SDK마다 서비스 신호 처리가 다르다
- <strong>C SDK</strong>는 `GO_AWAY`를 받으면 연결을 종료하고 상태 머신을 돌려 다시 연결하며, `RECONNECT_ICE_SERVER`를 받으면 ICE 설정을 다시 받는 상태로 넘어간다(소스 기준). 앱이 따로 처리할 것이 적다.
- <strong>JS SDK</strong>의 `SignalingClient`는 현재 master 브랜치 소스 기준으로 `SDP_OFFER`, `SDP_ANSWER`, `ICE_CANDIDATE`, `STATUS_RESPONSE`만 이벤트로 내보낸다. `GO_AWAY`와 `RECONNECT_ICE_SERVER`는 앱에 전달되지 않는다. 브라우저 앱은 `close` 이벤트를 기준으로 재연결해야 하고, TURN 교체는 ICE 상태 변화로 감지해야 한다.
:::

<strong>시그널링이 끊겨도 PeerConnection은 닫지 않는다.</strong> WebRTC 구조상 PeerConnection은 시그널링 연결과 독립이다. 앱이 시그널링 `close` 핸들러에서 PeerConnection까지 닫지만 않으면 미디어는 계속 흐를 수 있다. 다만 KVS 문서가 이 동작을 명시하지는 않으므로, 실제 디바이스로 "시그널링 재연결 중에도 영상이 끊기지 않는지"를 검증해 두어야 한다.

### 오류 처리

| 상황 | 신호 | 대응 |
|---|---|---|
| 채널 없음 | WSS 핸드셰이크 404 `ResourceNotFoundException` | 재시도해도 소용없다. 채널 프로비저닝·ARN 매핑을 확인한다 |
| 권한 없음·토큰 만료 | WSS 핸드셰이크 403 `AccessDeniedException`(컨트롤 플레인 API에서는 401) | 자격증명을 갱신하고 새로 서명한다. 반복되면 IAM 정책을 확인한다 |
| 연결 속도 초과·viewer 초과 | 400 `ClientLimitExceededException` | 지수 백오프 + 지터. viewer 수와 동시 재접속을 점검한다 |
| 잘못된 파라미터 | 400 `InvalidArgumentException` | ClientId 패턴(`AWS_` 접두사), ARN, `WEBRTC` 프로토콜 요청 여부를 확인한다 |
| 메시지 전달 실패 | `STATUS_RESPONSE`(correlationId를 넣었을 때만) | correlationId로 원래 메시지를 찾아 협상을 정리하거나 다시 시작한다 |
| 서비스 점검 | `GO_AWAY` | 60초 안에 재연결 |
| TURN 교체 | `RECONNECT_ICE_SERVER` | ICE 설정 재조회 + ICE restart |
| 1시간 경과 | 서버가 WebSocket을 닫는다 | 사전 재연결로 피한다 |
| idle 10분 | 서버가 WebSocket을 닫는다 | 위 역할별 정책 |
| 채널 수정 충돌 | `VersionMismatchException` | `DescribeSignalingChannel`로 최신 `Version`을 받아 다시 시도한다 |
| ICE 설정 조회 세션 만료 | `SessionExpiredException` | 채널에 다시 연결한다 |
| 서명 시각 오차(±5분 초과) | 핸드셰이크 실패(정확한 오류 코드는 문서에서 확인하지 못했다) | 디바이스 NTP 동기화, 브라우저 `systemClockOffset` |

브라우저에서는 위 표의 앞쪽 네 줄을 구분하기 어렵다. `WebSocket` API는 핸드셰이크 실패 시 HTTP 상태 코드를 노출하지 않고, 대개 `error` 다음 `close`(코드 1006)만 준다. 원인은 서버 쪽에서 찾아야 한다. 백엔드에서 `DescribeSignalingChannel`로 채널 상태를 확인하거나, CloudWatch의 시그널링 `Failure` 메트릭을 `Operation=ConnectAsViewer` 차원으로 보는 식이다([22장](/study/webrtc/22-kvs-operations)). Node.js `ws`처럼 핸드셰이크 응답을 볼 수 있는 클라이언트라면 `unexpected-response` 이벤트로 상태 코드를 바로 얻는다.

### 재연결 구현

브라우저 viewer용 재연결 래퍼다. 4절의 `requestSigner`를 쓰므로 연결을 열 때마다 백엔드가 같은 ClientId로 새 URL을 서명한다. `SignalingClient` 인스턴스는 한 번 닫히면 다시 열지 않고 매번 새로 만든다. 서명기에서 예외가 나면 `close` 없이 `error`만 발생하므로, 열리기 전의 `error`도 재시도 계기로 다룬다.

```js
class ViewerSignaling {
  constructor({ session, requestSigner, handlers }) {
    this.session = session;
    this.requestSigner = requestSigner;
    this.handlers = handlers;   // { onOpen(client), onAnswer, onCandidate, onStatus, needsSignaling() }
    this.current = null;
    this.attempt = 0;
    this.stopped = false;
  }

  start() { this.#open(); }

  stop() {
    this.stopped = true;
    clearTimeout(this.rotateTimer);
    clearTimeout(this.retryTimer);
    this.current?.close();
  }

  // 미디어 연결 후 idle로 닫혔다가 다시 시그널링이 필요해졌을 때 호출
  ensureConnected() { if (!this.current && !this.stopped) this.#open(); }

  #open() {
    const client = new KVSWebRTC.SignalingClient({
      channelARN: this.session.channelARN,
      channelEndpoint: this.session.wssEndpoint,
      clientId: this.session.clientId,          // 재연결에도 같은 ClientId
      role: KVSWebRTC.Role.VIEWER,
      region: this.session.region,
      requestSigner: this.requestSigner,
    });
    let opened = false;
    let failed = false;
    const fail = () => {
      if (failed || this.stopped) return;
      failed = true;
      if (this.current === client) this.current = null;
      if (!opened || this.handlers.needsSignaling()) this.#retry();   // 미디어 연결 후 idle이면 대기
    };

    client.on('open', () => {
      opened = true;
      const previous = this.current;
      this.current = client;
      previous?.close();                        // make-before-break: 새 연결이 열린 뒤 이전 연결 정리
      this.attempt = 0;
      this.#scheduleRotation();
      this.handlers.onOpen(client);
    });
    client.on('sdpAnswer', (answer) => this.handlers.onAnswer(answer));
    client.on('iceCandidate', (candidate) => this.handlers.onCandidate(candidate));
    client.on('statusResponse', (status) => this.handlers.onStatus?.(status));
    client.on('close', () => { if (client === this.current || !opened) fail(); });
    client.on('error', (err) => { console.warn('[signaling] error', err); if (!opened) fail(); });
    client.open();
  }

  #retry() {
    clearTimeout(this.retryTimer);
    const cap = Math.min(30_000, 1_000 * 2 ** this.attempt++);
    this.retryTimer = setTimeout(() => this.#open(), Math.random() * cap);   // 지수 백오프 + full jitter
  }

  #scheduleRotation() {
    clearTimeout(this.rotateTimer);
    const minutes = 40 + Math.random() * 5;     // 1시간 상한·45분 서술보다 여유 있게
    this.rotateTimer = setTimeout(() => {
      if (this.handlers.needsSignaling()) this.#open();
    }, minutes * 60_000);
  }
}
```

`needsSignaling()`은 앱이 판단한다. 예를 들어 PeerConnection의 `connectionState`가 `connected`가 아니거나 재협상을 앞두고 있으면 `true`를 돌려준다. ICE가 `disconnected`로 바뀌면 `ensureConnected()`를 불러 시그널링을 다시 열고 ICE restart offer를 보낸다. 디바이스(master) 쪽은 C SDK가 재연결 상태 머신을 내장하고 있으므로, 앱은 자격증명 갱신과 시계 동기화를 책임지면 된다([19장](/study/webrtc/19-kvs-c-sdk)).

::: tip 핵심 정리
- API는 계층이 셋이다. 컨트롤 플레인(`kinesisvideo`)에서 채널을 관리하고 엔드포인트를 받고, 채널 HTTPS 엔드포인트에서 `GetIceServerConfig`를 호출하고, 채널 WSS 엔드포인트에서 시그널링한다. 채널 엔드포인트는 `GetSignalingChannelEndpoint`로 채널·역할마다 받는다.
- 채널 생성·수정·삭제는 비동기다. 생성 후 `ACTIVE`를 기다리고, 수정에는 `CurrentVersion`이 필요하다.
- WSS 연결은 쿼리 문자열 SigV4 서명으로 인증한다. 서비스 이름은 `kinesisvideo`, 서명 헤더는 `host`, `X-Amz-Expires`는 JS SDK 기준 299초이고, 세션 토큰은 정규 요청에 포함해 서명한다. 시각 오차는 ±5분까지다.
- 송신은 `action`·`recipientClientId`·`messagePayload`(base64, 최대 10K)·`correlationId`, 수신은 `messageType`·`senderClientId`·`statusResponse`다. 실패 신호를 받으려면 `correlationId`를 넣어야 한다.
- ClientId는 동시 연결마다 유일하게, 재연결 시에는 그대로 유지한다. 백엔드가 정해서 서명하면 master가 `senderClientId`를 신뢰할 수 있다.
- 연결 1시간·idle 10분·GO_AWAY 유예 60초는 조정할 수 없다. 40분 무렵 make-before-break로 갈아타고, 실패 시 지수 백오프 + 지터로 재시도한다. JS SDK는 GO_AWAY를 앱에 전달하지 않으므로 `close` 기준으로 처리한다.
:::

## 다음 챕터

[디바이스 측 구현: KVS C SDK](/study/webrtc/19-kvs-c-sdk)에서는 master 쪽으로 넘어간다. C SDK의 구조와 의존성, `kvsWebrtcClientMaster` 샘플 흐름, GStreamer·하드웨어 인코더 연동, AWS IoT Credential Provider로 임시 자격증명을 받는 방법, 크로스 컴파일과 리소스 제약을 다룬다.

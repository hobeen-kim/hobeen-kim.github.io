---
title: "KVS 운영·보안·비용"
description: "KVS WebRTC를 실서비스로 굴릴 때 필요한 것들을 정리한다. 디바이스·운영자·프로비저닝 백엔드별 IAM 최소 권한 정책, 태그 기반 채널 수명관리, CloudWatch 메트릭과 SDK 로그, 과금 구조와 비용 추정, TURN 비용 최적화, 고정·증설 가능 할당량, 그리고 시계 오차·자격증명 만료·1시간 연결 한도·NAT 차단 같은 흔한 장애를 다룬다."
date: 2026-10-19
tags: [WebRTC, AWS, KinesisVideoStreams, IAM, CloudWatch, Cost]
prev: /study/webrtc/21-kvs-ingestion-storage
next: /study/webrtc/23-chime-sdk
---

# KVS 운영·보안·비용

::: info 학습 목표
- 디바이스(MASTER)·운영자(VIEWER)·프로비저닝 백엔드에 각각 필요한 KVS IAM 액션만 골라 최소 권한 정책을 쓸 수 있다.
- 디바이스 등록부터 폐기까지 채널·스트림·IoT 리소스의 수명을 태그로 관리하고, 고아 채널을 정리할 수 있다.
- CloudWatch 메트릭이 보여 주는 것과 보여 주지 못하는 것을 구분하고, SDK 로그로 빈자리를 채울 수 있다.
- 활성 채널·시그널링 메시지·TURN 분으로 월 비용을 추정하고, TURN 비중을 줄이는 방법을 안다.
- 조정 불가 할당량에 맞춰 설계하고, 시계 오차·자격증명 만료·1시간 연결 한도 같은 흔한 장애를 진단할 수 있다.
:::

## 1. IAM 최소 권한: 주체별로 나눈다

KVS WebRTC에 접근하는 주체는 성격이 전혀 다른 셋이다. 현장의 디바이스, 브라우저 앞의 운영자, 채널을 만들고 지우는 백엔드다. 하나의 넓은 정책을 셋이 같이 쓰면, 디바이스 하나가 탈취됐을 때 공격자가 다른 농기계 채널에 viewer로 붙거나 채널을 지울 수 있다. 원칙은 단순하다. <strong>주체마다 역할을 나누고, 역할마다 필요한 액션과 리소스만 허용한다.</strong>

![주체별 자격증명 경로와 허용 범위. 농기계 디바이스는 X.509 인증서로 IoT Credentials Provider의 role alias를 거쳐 device-master 역할을 받고, ConnectAsMaster·GetIceServerConfig·GetSignalingChannelEndpoint·Describe 액션을 channel/${ThingName}/* 리소스에만 쓴다. 운영자 브라우저는 백엔드의 STS AssumeRole로 채널 하나로 좁힌 세션 정책을 받아 operator-viewer 역할로 ConnectAsViewer 등을 channel/tractor-001/*에만 쓴다. 프로비저닝 백엔드는 장기 액세스 키 없이 서비스 실행 역할로 channel-admin 권한을 받아 Create·Delete·Tag·List와 MediaStorageConfiguration 액션을 aws:RequestTag 조건 아래 channel/*와 stream/*에 쓴다](/images/study-webrtc/22-iam-principals-light.png)
![주체별 자격증명 경로와 허용 범위. 농기계 디바이스는 X.509 인증서로 IoT Credentials Provider의 role alias를 거쳐 device-master 역할을 받고, ConnectAsMaster·GetIceServerConfig·GetSignalingChannelEndpoint·Describe 액션을 channel/${ThingName}/* 리소스에만 쓴다. 운영자 브라우저는 백엔드의 STS AssumeRole로 채널 하나로 좁힌 세션 정책을 받아 operator-viewer 역할로 ConnectAsViewer 등을 channel/tractor-001/*에만 쓴다. 프로비저닝 백엔드는 장기 액세스 키 없이 서비스 실행 역할로 channel-admin 권한을 받아 Create·Delete·Tag·List와 MediaStorageConfiguration 액션을 aws:RequestTag 조건 아래 channel/*와 stream/*에 쓴다](/images/study-webrtc/22-iam-principals-dark.png)

### 정책을 쓰기 전에 알아둘 IAM 사실

AWS Service Authorization Reference(Kinesis Video Streams 항목) 기준으로 정리하면 다음과 같다.

| 항목 | 내용 |
|---|---|
| 채널 리소스 ARN | `arn:${Partition}:kinesisvideo:${Region}:${Account}:channel/${ChannelName}/${CreationTime}` |
| 스트림 리소스 ARN | `arn:${Partition}:kinesisvideo:${Region}:${Account}:stream/${StreamName}/${CreationTime}` |
| 채널 대상 액션 | `ConnectAsMaster`, `ConnectAsViewer`, `GetSignalingChannelEndpoint`, `GetIceServerConfig`, `DescribeSignalingChannel`, `UpdateSignalingChannel`, `DeleteSignalingChannel`, `UpdateMediaStorageConfiguration`, `DescribeMediaStorageConfiguration`, `JoinStorageSession`, `JoinStorageSessionAsViewer` 등. 모두 `aws:ResourceTag/${TagKey}` 조건을 지원한다 |
| 리소스 없는 액션 | `ListSignalingChannels`, `ListStreams`는 리소스 타입이 없어 `"Resource": "*"`로만 허용할 수 있다 |
| 생성 시 태그 | `CreateSignalingChannel` API는 `kinesisvideo:CreateSignalingChannel`과 함께 `kinesisvideo:TagResource`를 요구한다(태그를 붙일 때). `CreateStream`은 `TagStream`을 함께 요구한다. 생성 액션은 `aws:RequestTag`, `aws:TagKeys` 조건을 지원한다 |

ARN 끝에 생성 시각이 붙는다는 점이 중요하다. 같은 이름으로 채널을 지웠다 다시 만들면 ARN이 바뀐다. 그래서 정책에는 `channel/tractor-001/*`처럼 <strong>이름 뒤를 와일드카드</strong>로 둔다. ARN 전체를 정책에 박아 두면 채널을 재생성하는 순간 권한이 끊긴다.

### 디바이스용 MASTER 정책

디바이스는 [19장](/study/webrtc/19-kvs-c-sdk)에서 본 AWS IoT Credential Provider로 임시 자격증명을 받는다. 이 역할에 붙이는 권한 정책은 다음과 같다. IAM 정책 변수 `${credentials-iot:ThingName}`으로 "자기 이름의 채널에만" 붙게 만든다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SignalingAsMasterOnOwnChannel",
      "Effect": "Allow",
      "Action": [
        "kinesisvideo:DescribeSignalingChannel",
        "kinesisvideo:DescribeMediaStorageConfiguration",
        "kinesisvideo:GetSignalingChannelEndpoint",
        "kinesisvideo:GetIceServerConfig",
        "kinesisvideo:ConnectAsMaster"
      ],
      "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/${credentials-iot:ThingName}/*"
    },
    {
      "Sid": "StorageModeDevicesOnly",
      "Effect": "Allow",
      "Action": "kinesisvideo:JoinStorageSession",
      "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/${credentials-iot:ThingName}/*"
    },
    {
      "Sid": "ProducerSdkRecordingOnOwnStream",
      "Effect": "Allow",
      "Action": [
        "kinesisvideo:DescribeStream",
        "kinesisvideo:GetDataEndpoint",
        "kinesisvideo:PutMedia"
      ],
      "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:stream/${credentials-iot:ThingName}-rec/*"
    }
  ]
}
```

이 정책에서 의도적으로 빼거나 넣은 것들이 있다.

- <strong>`CreateSignalingChannel`을 뺐다.</strong> KVS C SDK README의 IoT 예시 정책에는 `CreateSignalingChannel`이 들어 있다. 샘플이 채널이 없으면 직접 만들기 때문이다. 운영에서는 채널을 백엔드가 미리 만들고 디바이스는 쓰기만 하게 하는 편이 낫다. 디바이스가 채널을 만들 수 있으면 인증서 하나로 채널 수 할당량을 소진하는 공격도 가능해진다.
- <strong>`DescribeMediaStorageConfiguration`을 넣었다.</strong> C SDK 샘플의 기본 캐시 정책(`SIGNALING_API_CALL_CACHE_TYPE_FILE_EXCEPT_DESCRIBE_MEDIA`)은 연결할 때마다 이 API로 저장 모드 여부를 확인한다.
- `JoinStorageSession`은 저장 모드([21장](/study/webrtc/21-kvs-ingestion-storage))를 쓰는 디바이스에만, `PutMedia` 묶음은 Producer SDK로 병행 녹화하는 디바이스에만 둔다. 쓰지 않는 문은 닫는다.

`${credentials-iot:ThingName}`에는 함정이 두 가지 있다. 이 변수는 <strong>IAM 정책에서만</strong> 동작하고 IoT Core 정책에서는 쓸 수 없다. 그리고 디바이스가 자격증명을 요청할 때 `x-amzn-iot-thingname` 헤더를 보내야만 값이 채워진다. 헤더의 thing 이름이 인증서에 붙은 thing과 다르면 403이 난다. 채널 이름을 thing 이름과 같게 하라는 권장("KVS recommendation is to use iot thing name as channel name")과 채널용 정책 예시는 awslabs C SDK README에 있고, KVS 개발자 가이드의 IoT 예시는 스트림(`stream/${credentials-iot:ThingName}/*`) 기준이다.

역할 쪽 설정도 짝을 맞춘다. 먼저 device-master 역할의 신뢰 정책이다. IoT credentials provider만 이 역할을 맡을 수 있게 한다.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "credentials.iot.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

디바이스 인증서에 붙이는 IoT Core 정책에는 role alias로 자격증명을 받을 권한만 준다.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "iot:AssumeRoleWithCertificate",
    "Resource": "arn:aws:iot:ap-northeast-2:123456789012:rolealias/kvs-device-master"
  }]
}
```

role alias의 `credentialDurationSeconds`는 900~43,200초(기본 3,600초)이고 역할의 최대 세션 시간 이하여야 한다. 길게 잡으면 탈취된 자격증명의 수명도 길어진다. 인증서·thing·정책 연결 방식은 [AWS IoT Core 완전 정복](/posts/tech/2025-06-27-iot) 포스트에서 다뤘다.

### 운영자용 VIEWER 정책

운영자 브라우저에는 [20장](/study/webrtc/20-kvs-viewer-backend)에서 설계한 대로 백엔드가 STS로 짧은 임시 자격증명을 발급한다. 역할 정책은 넓게(태그 조건), 발급 시 세션 정책으로 좁게(채널 하나) 두 겹으로 거른다. 유효 권한은 두 정책의 교집합이다. 아래 operator-viewer 역할 정책은 `env=prod` 태그가 붙은 채널에 대해서만 viewer 액션을 허용한다.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ViewerOnProdChannels",
    "Effect": "Allow",
    "Action": [
      "kinesisvideo:DescribeSignalingChannel",
      "kinesisvideo:GetSignalingChannelEndpoint",
      "kinesisvideo:GetIceServerConfig",
      "kinesisvideo:ConnectAsViewer",
      "kinesisvideo:JoinStorageSessionAsViewer"
    ],
    "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/*",
    "Condition": { "StringEquals": { "aws:ResourceTag/env": "prod" } }
  }]
}
```

```js
// 백엔드: 운영자가 권한을 가진 디바이스인지 확인한 뒤, 그 채널 하나로 좁혀 발급
import { STSClient, AssumeRoleCommand } from '@aws-sdk/client-sts';

const region = 'ap-northeast-2';
const accountId = process.env.AWS_ACCOUNT_ID;
const sts = new STSClient({ region });

export async function issueViewerCredentials(operatorId, channelName) {
  const sessionPolicy = {
    Version: '2012-10-17',
    Statement: [{
      Effect: 'Allow',
      Action: [
        'kinesisvideo:DescribeSignalingChannel',
        'kinesisvideo:GetSignalingChannelEndpoint',
        'kinesisvideo:GetIceServerConfig',
        'kinesisvideo:ConnectAsViewer',
      ],
      Resource: `arn:aws:kinesisvideo:${region}:${accountId}:channel/${channelName}/*`,
    }],
  };
  const { Credentials } = await sts.send(new AssumeRoleCommand({
    RoleArn: process.env.OPERATOR_VIEWER_ROLE_ARN,
    RoleSessionName: `op-${operatorId}`.slice(0, 64),   // CloudTrail에서 누가 붙었는지 추적
    Policy: JSON.stringify(sessionPolicy),
    DurationSeconds: 900,                               // AssumeRole 최소값
  }));
  return Credentials;
}
```

녹화 재생(HLS URL 발급, `GetClip`)은 브라우저에 권한을 주지 말고 백엔드가 대신 호출해 URL만 넘긴다([21장](/study/webrtc/21-kvs-ingestion-storage) 1절). 스트림 권한까지 브라우저로 내보낼 이유가 없다.

### 프로비저닝 백엔드 정책

채널을 만들고 지우는 백엔드는 가장 강한 권한을 가지므로 <strong>태그 조건으로 자기 소유 리소스에만</strong> 손대게 한다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CreateOnlyWithManagedTags",
      "Effect": "Allow",
      "Action": ["kinesisvideo:CreateSignalingChannel", "kinesisvideo:TagResource"],
      "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/*",
      "Condition": {
        "StringEquals": { "aws:RequestTag/managed-by": "device-provisioner" },
        "ForAllValues:StringEquals": { "aws:TagKeys": ["managed-by", "fleet", "device-id", "env"] }
      }
    },
    {
      "Sid": "ManageOwnChannels",
      "Effect": "Allow",
      "Action": [
        "kinesisvideo:DescribeSignalingChannel",
        "kinesisvideo:UpdateSignalingChannel",
        "kinesisvideo:DeleteSignalingChannel",
        "kinesisvideo:ListTagsForResource",
        "kinesisvideo:UpdateMediaStorageConfiguration",
        "kinesisvideo:DescribeMediaStorageConfiguration"
      ],
      "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/*",
      "Condition": { "StringEquals": { "aws:ResourceTag/managed-by": "device-provisioner" } }
    },
    {
      "Sid": "ListHasNoResourceType",
      "Effect": "Allow",
      "Action": "kinesisvideo:ListSignalingChannels",
      "Resource": "*"
    },
    {
      "Sid": "RecordingStreams",
      "Effect": "Allow",
      "Action": [
        "kinesisvideo:CreateStream",
        "kinesisvideo:TagStream",
        "kinesisvideo:DescribeStream",
        "kinesisvideo:UpdateDataRetention",
        "kinesisvideo:DeleteStream"
      ],
      "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:stream/*-rec/*"
    }
  ]
}
```

- 첫 문장은 `managed-by=device-provisioner` 태그 없이는 채널을 못 만들게 하고, 허용된 태그 키 외에는 붙이지 못하게 한다.
- `UntagResource`는 일부러 뺐다. 백엔드 버그로 `managed-by` 태그가 지워지면 이 정책의 둘째 문장이 그 채널을 관리하지 못하게 되기 때문이다. 태그 수정이 필요하면 별도 운영 역할로 한다.
- 이 백엔드는 ECS 태스크 역할이나 Lambda 실행 역할로 돌려서 장기 액세스 키를 아예 만들지 않는다.

## 2. 채널 수명관리: 만들고, 표시하고, 지운다

채널은 디바이스와 수명을 같이해야 한다. 디바이스 등록 시점에 만들고, 폐기 시점에 지운다. [20장](/study/webrtc/20-kvs-viewer-backend)에서 등록 쪽을 다뤘으니 여기서는 태그 설계와 폐기·정리를 다룬다.

### 왜 지워야 하나

과금만 보면 채널을 지울 이유가 약해 보인다. 활성 채널 요금은 <strong>그 달에 디바이스나 앱이 한 번이라도 연결한 채널</strong>에만 붙기 때문이다. 연결이 없는 채널은 그 달 요금이 0이다. 그래도 지워야 하는 이유는 따로 있다.

- <strong>할당량</strong>: 계정·리전당 채널 수 한도가 있다. 문서끼리 숫자가 다르다(WebRTC 개발자 가이드는 us-east-1·us-west-2 10,000 / 그 외 5,000, General Reference는 20,000 / 10,000). 저장 설정 채널은 기본 100개다. 고아 채널이 쌓이면 신규 등록이 막힌다.
- <strong>보안</strong>: 폐기한 디바이스의 인증서가 살아 있고 채널도 남아 있으면, 그 인증서를 손에 넣은 누군가가 master로 붙어 "폐기된 트랙터" 행세를 할 수 있다. 채널 삭제와 인증서 폐기는 같이 간다.
- <strong>저장 비용</strong>: 채널에 연결된 스트림은 별개 리소스다. 채널을 지워도 스트림과 보존 중인 데이터는 남아 저장 요금이 계속 나간다.
- <strong>이름 재사용</strong>: 같은 thing 이름으로 디바이스를 다시 등록할 때 이전 채널이 남아 있으면 메시지 TTL·저장 설정 같은 이전 상태를 물려받는다.

### 태그 설계

채널에는 태그를 최대 50개 붙일 수 있다. 이 스터디의 예시는 네 개만 쓴다.

| 키 | 예시 값 | 쓰임 |
|---|---|---|
| `managed-by` | `device-provisioner` | IAM 조건(1절), 정리 작업의 대상 판별 |
| `device-id` | `tractor-001` | 디바이스 레지스트리와 대조 |
| `fleet` | `jeonbuk-farm-a` | 고객·농장 단위 집계, 비용 배분 |
| `env` | `prod` / `staging` | 운영자 정책 조건, 환경 분리 |

`fleet`을 농장별 비용 집계에 쓰려면 Billing 콘솔에서 비용 배분 태그로 활성화해야 한다. KVS 채널 요금이 실제로 태그별로 나뉘어 잡히는지는 첫 달 청구 내역으로 확인한다.

### 폐기 순서

디바이스 한 대를 폐기할 때의 순서는 다음과 같다. 순서가 중요하다.

1. <strong>IoT 인증서를 비활성화·폐기</strong>한다(`aws iot update-certificate --new-status REVOKED`). 새 자격증명 발급을 먼저 막아야 이후 단계 중에 디바이스가 다시 붙지 않는다.
2. <strong>저장 모드를 끈다</strong>(`UpdateMediaStorageConfiguration`, `Status=DISABLED`). `DeleteSignalingChannel` API의 오류 목록에는 저장 매핑과 관련된 `ResourceInUseException`이 있으므로, 매핑을 먼저 풀고 지우는 편이 안전하다.
3. <strong>채널을 삭제</strong>한다. `DeleteSignalingChannel`은 비동기 작업이라 잠시 `DELETING` 상태를 거친다. `CurrentVersion`을 넘기면 그 사이 누가 채널을 바꿨을 때 `VersionMismatchException`으로 막을 수 있다.
4. <strong>녹화 스트림을 처리</strong>한다. 사고 조사용으로 남겨야 할 구간이 있으면 `GetClip`으로 내려받아 S3 등에 옮긴 뒤 `DeleteStream`을 호출한다.
5. IoT thing·정책 연결을 정리하고 디바이스 레지스트리 상태를 `retired`로 바꾼다.

### 고아 채널 정리 작업

레지스트리와 실제 채널은 언젠가 어긋난다. 등록 중 실패, 수동 테스트, 레지스트리 버그 때문이다. 주기적으로 대조해 정리하는 작업을 둔다.

```js
// Node.js (AWS SDK v3) — 레지스트리에 없는 채널을 찾아 정리. 기본은 dry-run
import {
  KinesisVideoClient, ListSignalingChannelsCommand, ListTagsForResourceCommand,
  DescribeMediaStorageConfigurationCommand, UpdateMediaStorageConfigurationCommand,
  DeleteSignalingChannelCommand,
} from '@aws-sdk/client-kinesis-video';

const kv = new KinesisVideoClient({ region: 'ap-northeast-2' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function sweepOrphanChannels(isRegisteredDevice, { dryRun = true } = {}) {
  let NextToken;
  do {
    const page = await kv.send(new ListSignalingChannelsCommand({
      ChannelNameCondition: { ComparisonOperator: 'BEGINS_WITH', ComparisonValue: 'tractor-' },
      MaxResults: 500,
      NextToken,
    }));
    for (const ch of page.ChannelInfoList ?? []) {
      const { Tags = {} } = await kv.send(new ListTagsForResourceCommand({ ResourceARN: ch.ChannelARN }));
      if (Tags['managed-by'] !== 'device-provisioner') continue;   // 다른 시스템의 채널은 건드리지 않는다
      if (await isRegisteredDevice(Tags['device-id'])) continue;
      console.log('orphan channel', ch.ChannelName, dryRun ? '(dry-run)' : '→ delete');
      if (!dryRun) await retireChannel(ch.ChannelARN, ch.Version);
      await sleep(250);   // Delete/Tag/ListTags 계열: 계정 50 TPS, 리소스당 5 TPS
    }
    NextToken = page.NextToken;
  } while (NextToken);
}

export async function retireChannel(channelArn, version) {
  const { MediaStorageConfiguration: msc } = await kv.send(
    new DescribeMediaStorageConfigurationCommand({ ChannelARN: channelArn }));
  if (msc?.Status === 'ENABLED') {
    await kv.send(new UpdateMediaStorageConfigurationCommand({
      ChannelARN: channelArn,
      MediaStorageConfiguration: { Status: 'DISABLED' },
    }));
  }
  await kv.send(new DeleteSignalingChannelCommand({ ChannelARN: channelArn, CurrentVersion: version }));
}
```

삭제는 되돌릴 수 없으므로 dry-run 결과를 사람이 확인한 뒤에만 실제 삭제를 돌린다. 반대 방향(레지스트리에는 있는데 채널이 없는 디바이스)도 같은 작업에서 찾아 재생성 큐에 넣으면 대조가 완성된다.

## 3. 관측: CloudWatch 메트릭과 SDK 로그

### CloudWatch가 보여 주는 것

KVS WebRTC 개발자 가이드의 모니터링 문서에 나오는 메트릭은 세 묶음이다.

| 묶음 | 메트릭 | 차원(Dimension) | 읽는 법 |
|---|---|---|---|
| 시그널링 | `Failure`(Count, 200이면 0 아니면 1), `Latency`(ms), `MessagesTransferred.Count` | `Operation`, `SignalingChannelName` | `Operation` 값: ConnectAsMaster, ConnectAsViewer, SendSdpOffer, SendSdpAnswer, SendCandidate, SendAlexaOfferToMaster, GetIceServerConfig, Disconnect |
| TURN | `TURNConnectedMinutes`(Count, 1분 동안 데이터가 흐른 allocation마다 1) | `SignalingChannelName` | TURN 과금 분과 직결된다 |
| ingestion | `Failure`, `Latency`, `TotalBitrate`(bps), `TotalPacketCount`, `WebRTCRecordingMinutes`, `WebRTCViewerMinutes` | `Operation`(JoinStorageSession / JoinStorageSessionAsViewer), `SignalingChannelName`, `Role`(MASTER / VIEWER) | 저장 모드 과금 분과 직결된다 |

메트릭은 15개월 보관된다. 모니터링 문서 본문에서는 이 메트릭의 <strong>네임스페이스 문자열을 확인하지 못했다</strong>. 추측해서 알람을 만들지 말고, 메트릭 이름으로 실제 네임스페이스부터 조회한다.

```bash
# 메트릭 이름으로 네임스페이스·차원을 확인한 뒤 알람·대시보드를 만든다
aws cloudwatch list-metrics --metric-name TURNConnectedMinutes --region ap-northeast-2
aws cloudwatch list-metrics --metric-name MessagesTransferred.Count --region ap-northeast-2
```

이 메트릭으로 걸 만한 알람은 다음과 같다.

| 신호 | 의미 | 대응 |
|---|---|---|
| `Failure`(`Operation=ConnectAsMaster`)가 특정 채널에서 반복 | 그 디바이스의 자격증명·시계·정책 문제 | 7절 표로 진단 |
| `Failure`(`Operation=ConnectAsViewer`) 급증 | viewer 한도 초과(`ClientLimitExceededException`) 또는 운영자 자격증명 문제 | 백엔드 좌석 관리 확인 |
| `MessagesTransferred.Count`가 평소의 몇 배 | 재연결 폭주(무한 재시도 루프)일 가능성 | 백오프 로직 점검 |
| `TURNConnectedMinutes` 합계 추세 상승 | relay 비율 증가 → 비용 증가 | 5절 최적화 |
| `WebRTCRecordingMinutes`가 작업 시간과 안 맞음 | 저장 세션 재참여 실패로 녹화가 비어 있음 | 디바이스 1시간 재참여 로직 확인 |

채널이 수백 개면 채널별 알람을 하나씩 만들기보다, 함대 전체 합계 알람 하나와 "상위 N개 채널" 대시보드(CloudWatch 메트릭 수식의 `SEARCH`)를 두는 편이 관리하기 쉽다.

### CloudWatch가 보여 주지 못하는 것

기본 모드에서 미디어는 피어끼리 직접 흐른다. AWS는 그 경로를 보지 못하므로 <strong>RTT·지터·손실·프레임 드롭 같은 품질 지표는 CloudWatch에 없다</strong>. 품질은 양 끝에서 모아야 한다.

- <strong>브라우저</strong>: `getStats()`로 candidate-pair·inbound-rtp 지표를 주기적으로 모아 백엔드로 보낸다. 무엇을 볼지는 [15장](/study/webrtc/15-monitoring-debugging)에 정리했다.
- <strong>디바이스(C SDK)</strong>: `rtcPeerConnectionGetMetrics()`로 같은 종류의 통계를 얻는다. 샘플 코드는 이 API로 선택된 로컬·원격 후보 타입(`candidateType`)을 로그로 찍는다. `signalingClientGetMetrics()`는 시그널링 단계별 소요 시간을 준다.
- 세션 종료 시 "선택된 후보 쌍이 relay였는가"를 한 줄 이벤트로 남겨 두면, 5절의 TURN 비율을 디바이스·통신사·농장별로 쪼개 볼 수 있다.

수집한 지표를 메트릭·로그·트레이스로 다루는 방법은 [관측성 스터디](/study/observability/)를 참고한다.

### SDK 로그

KVS C SDK의 로그 설정은 다음과 같다.

| 설정 | 값 | 비고 |
|---|---|---|
| `AWS_KVS_LOG_LEVEL` | 1 VERBOSE, 2 DEBUG, 3 INFO, 4 WARN, 5 ERROR, 6 FATAL, 7 SILENT, 8 PROFILE | 기본 WARN(4) |
| 연결 타이밍 로그 | v1.8.0부터 기본으로 `kvsFileLogFilter.x` 파일 생성 | 연결 수립 단계별 소요 시간 |
| 파일 로깅 | README 본문은 `AWS_ENABLE_FILE_LOGGING=TRUE`, 환경변수 표는 `ENABLE_FILE_LOGGING`으로 적는다 | 표기가 다르므로 쓰는 버전의 샘플 코드를 확인 |
| `KVS_ICE_TRANSPORT_POLICY` | `all`(기본) / `relay` | `relay`는 TURN 경로 강제 테스트용 |

평소에는 WARN으로 두고, 문제 디바이스만 원격 설정으로 DEBUG·VERBOSE로 올린다. VERBOSE는 함수 진입·종료까지 찍어 SD 카드를 금방 채운다. AWS 지원에 저장 모드 문제를 문의할 때 C SDK README가 요구하는 정보는 채널 ARN, 스트림 ARN, 테스트 시간 범위, SDK 버전, VERBOSE 로그 등이다. 이 정보를 디바이스에서 원격으로 수집하는 경로를 미리 만들어 두면 장애 대응 시간이 줄어든다.

JS SDK 쪽에서는 `statusResponse` 이벤트를 반드시 로그로 남긴다. 실패한 메시지에 `correlationId`를 넣었을 때만 오는 응답이라, 이 로그가 없으면 "왜 안 붙는지"를 서버 쪽 근거 없이 추측해야 한다.

## 4. 비용 구조와 추정

### 무엇에 돈이 나가나

![KVS WebRTC 과금 지점. 디바이스(master)와 운영자(viewer)가 시그널링 채널을 통해 SDP와 ICE를 주고받는 부분에는 활성 채널 월 요금과 100만 건당 메시지 요금이 붙는다. 두 피어가 host나 srflx 후보로 직접 P2P 연결되면 KVS 미디어 요금이 없다. 직결이 안 되어 KVS TURN을 거치면 TURN 분 요금과 인터넷 데이터 전송 요금이 붙는다. 저장 모드에서는 storage 세션과 Video Stream에 녹화 분, 실시간 viewer 분, 저장 GB-월 요금이 붙는다](/images/study-webrtc/22-billing-points-light.png)
![KVS WebRTC 과금 지점. 디바이스(master)와 운영자(viewer)가 시그널링 채널을 통해 SDP와 ICE를 주고받는 부분에는 활성 채널 월 요금과 100만 건당 메시지 요금이 붙는다. 두 피어가 host나 srflx 후보로 직접 P2P 연결되면 KVS 미디어 요금이 없다. 직결이 안 되어 KVS TURN을 거치면 TURN 분 요금과 인터넷 데이터 전송 요금이 붙는다. 저장 모드에서는 storage 세션과 Video Stream에 녹화 분, 실시간 viewer 분, 저장 GB-월 요금이 붙는다](/images/study-webrtc/22-billing-points-dark.png)

가격은 AWS Price List API의 2026-09-30 게시분 기준이다(USD).

| 항목 | us-east-1 | ap-northeast-2(서울) | 과금 규칙 |
|---|---|---|---|
| 활성 시그널링 채널 | $0.03 / 채널·월 | $0.04 / 채널·월 | 그 달에 한 번이라도 연결된 채널 |
| 시그널링 메시지 | $2.25 / 100만 건 | $2.75 / 100만 건 | 송신·수신 중 어느 쪽으로 세는지는 문서에서 확인하지 못함 |
| TURN 스트리밍 | $0.12 / 1,000분 | $0.15 / 1,000분 | 1분 단위 계량. relay 데이터가 AWS 밖으로 나가면 표준 데이터 전송 요금 별도 |
| 저장 모드 녹화(`WebRTCRecording`) | $0.0034 / 분 | $0.0038 / 분 | WebRTC로 스트림에 녹화된 미디어 분 |
| 저장 모드 실시간 viewer(`WebRTCViewer`) | $0.003 / 분 | $0.0035 / 분 | 1080p 이하 실시간 viewer 분 |

저장 모드 두 항목은 KVS 가격 페이지 HTML 본문에는 보이지 않고 Price List API에서만 확인된다. 서울 요금은 항목에 따라 us-east-1보다 약 10~30% 높다.

### 계산 방법 검증: 가격 페이지 예시

계산법이 맞는지 가격 페이지 예시로 먼저 맞춰 본다(us-east-1).

| 예시 | 활성 채널 | 메시지 | TURN | 합계 |
|---|---|---|---|---|
| 스마트폰 앱 100명 | 100 × $0.03 = $3.00 | 15만 ÷ 100만 × $2.25 = $0.34 | 40,000 ÷ 1,000 × $0.12 = $4.80 | <strong>$8.14</strong> |
| 홈 카메라 1,000대 | 1,000 × $0.03 = $30.00 | 300만 ÷ 100만 × $2.25 = $6.75 | 80,000 ÷ 1,000 × $0.12 = $9.60 | <strong>$46.35</strong> |

두 예시 모두 가격 페이지의 합계와 일치한다. 같은 방식으로 농기계 플랫폼을 추정해 보자.

### 농기계 200대 추정 (서울 리전, 2026-09-30 가격)

가정은 다음과 같다. 숫자보다 <strong>가정이 바뀌면 결과가 어떻게 바뀌는지</strong>를 보는 것이 목적이다.

- 디바이스 200대, 모두 매달 연결한다.
- 운영자가 디바이스마다 하루 3번, 한 번에 20분 실시간으로 본다. 한 달 30일이면 디바이스당 90세션, 전체 18,000세션이다.
- 세션당 시그널링 메시지는 offer 1 + answer 1 + ICE 후보 양쪽 합계 약 18건으로 20건이라고 둔다. 송·수신 집계 방식을 모르니 보수적으로 두 배(40건)로 잡는다.
- 세션의 20%가 TURN을 쓰고, relay 세션은 보수적으로 양쪽 모두 allocation을 잡는다고 본다(allocation 2개 × 20분).

| 단계 | 계산 | 결과 |
|---|---|---|
| ① 활성 채널 | 200 × $0.04 | $8.00 |
| ② 메시지 수 | 18,000세션 × 40건 | 720,000건 |
| ③ 메시지 요금 | 0.72 × $2.75 | $1.98 |
| ④ relay 세션 | 18,000 × 20% | 3,600세션 |
| ⑤ TURN 분 | 3,600 × 20분 × allocation 2 | 144,000분 |
| ⑥ TURN 요금 | 144 × $0.15 | $21.60 |
| <strong>월 합계(데이터 전송 제외)</strong> | ① + ③ + ⑥ | <strong>$31.58</strong> |

같은 가정을 us-east-1 요금으로 계산하면 $6.00 + $1.62 + $17.28 = $24.90이다.

이 표에서 읽어야 할 것은 두 가지다.

1. <strong>TURN이 지배한다.</strong> relay 비율이 20%만 돼도 TURN이 전체의 70% 가까이를 차지한다. relay 비율이 60%로 오르면(LTE CGNAT 환경에서 흔히 생길 수 있는 상황) TURN 분은 432,000분, 요금은 $64.80이 되고 합계는 $74.78로 두 배 이상이 된다.
2. <strong>TURN 분 요금보다 데이터 전송량이 더 클 수 있다.</strong> relay된 데이터가 인터넷으로 나가면 표준 데이터 전송 요금이 별도로 붙는다([KVS 가격 페이지](https://aws.amazon.com/kinesis/video-streams/pricing/)의 WebRTC 예시에 명시). 2 Mbps 영상 20분은 약 300 MB다(2 Mbps × 1,200초 = 2,400 Mb). 3,600세션이면 약 1,080 GB, 1 TB가 넘는다. GB당 요율이 센트 단위만 돼도 TB 단위 송신은 위 표의 TURN 분 요금(수십 달러)을 쉽게 넘는다. 요율은 리전별 데이터 전송 요금표에서 확인한다(서울 인터넷 송신 첫 10 TB $0.126/GB로 계산한 예는 [25장](/study/webrtc/25-capstone-farm-platform) 6절).

저장 모드를 켠 채널은 여기에 분당 녹화·viewer 요금이 더해진다. 상시 녹화라면 이 항목이 전체 비용을 압도할 수 있다는 계산은 [21장](/study/webrtc/21-kvs-ingestion-storage) 6절에서 했다.

## 5. TURN 비용 최적화: 직접 P2P 비율 높이기

TURN은 비용만의 문제가 아니다. TURN 세션은 대역폭이 <strong>5 Mbps로 고정</strong>(조정 불가)이고 채널당 동시 allocation은 50개다. relay를 거치면 지연도 늘어난다. 직접 P2P 비율을 높이는 것은 비용·품질·한도 모두에 이득이다.

### 먼저 잰다

최적화는 측정에서 시작한다.

- 채널별 `TURNConnectedMinutes`로 "어느 디바이스가 relay를 많이 쓰는가"를 본다.
- 세션마다 선택된 후보 쌍의 타입(브라우저 `getStats()`의 local/remote candidate `candidateType`, C SDK `rtcPeerConnectionGetMetrics()`)을 기록해 relay 비율을 통신사·농장·운영자 네트워크별로 나눈다. relay가 "디바이스 쪽 NAT" 때문인지 "운영자 사무실 방화벽" 때문인지에 따라 처방이 다르다.

### 줄이는 방법

| 방법 | 효과 | 주의 |
|---|---|---|
| `iceTransportPolicy`를 `all`(기본)로 둔다 | relay 강제를 피한다 | C SDK `KVS_ICE_TRANSPORT_POLICY=relay`나 브라우저 `relay` 설정이 테스트 후 그대로 남아 있지 않은지 점검한다 |
| STUN을 항상 함께 넣는다 | srflx 후보로 홀펀칭 기회를 만든다 | KVS는 STUN을 `GetIceServerConfig`로 주지 않는다. `stun:stun.kinesisvideo.{region}.amazonaws.com:443`을 직접 넣어야 한다([18장](/study/webrtc/18-kvs-signaling-api)) |
| 운영자 네트워크에서 UDP 아웃바운드 허용 | 사무실 방화벽이 UDP를 막으면 TURN TCP/TLS로 떨어진다 | IT 팀과 협의. 최소한 STUN의 UDP 443과 P2P용 UDP 아웃바운드 |
| 디바이스 회선 개선 | LTE CGNAT은 symmetric NAT 동작이 많아 직결이 어렵다([05장](/study/webrtc/05-nat-stun)) | 통신사 APN·요금제에 따라 다르다. 고정 공인 IP나 NAT 동작이 완화된 회선을 검토한다 |
| IPv6 dual-stack 검토 | 양쪽 모두 IPv6면 NAT 없이 직결될 수 있다 | C SDK v1.20(`KVS_DUALSTACK_ENDPOINTS=ON`)·JS SDK는 dual-stack 모드를 제공하지만, System requirements 문서는 STUN/TURN IPv6 미지원이라고 적는다. 문서끼리 맞지 않으므로 대상 리전에서 실측한다 |
| 쓰지 않는 세션을 닫는다 | TURN 분은 데이터가 흐르는 동안 쌓인다 | 탭이 숨겨진 채 20분 넘게 지나면 PeerConnection을 닫고 "계속 보기" 버튼을 띄운다(Page Visibility API). 디바이스 업링크도 같이 아낀다 |
| relay 세션 비트레이트 상한 | TURN 분은 줄지 않지만 데이터 전송 GB가 준다 | relay로 판정되면 `maxBitrate`를 낮춘다([09장](/study/webrtc/09-quality-latency)). 어차피 5 Mbps 상한이 있다 |

TURN 서버를 직접 운영하는 선택지(coturn, [07장](/study/webrtc/07-turn))도 있지만, KVS 관리형 TURN은 채널 인증·자격증명 발급과 묶여 있다. 직접 TURN을 섞으면 그 인증과 가용성을 직접 책임져야 하므로, relay 트래픽이 정말 커졌을 때 비용을 비교해 판단한다.

## 6. 할당량 관리: 고정 한도와 증설 가능한 한도

할당량은 두 부류로 나눠 대한다. <strong>증설 가능한 한도(soft)</strong>는 사용량 예측과 사전 신청으로 해결하고, <strong>조정 불가 한도(hard)</strong>는 설계로 피한다.

| 항목 | 값 | 조정 | 설계 영향 |
|---|---|---|---|
| 시그널링 채널 수(계정·리전) | 문서마다 다름(10,000/5,000 또는 20,000/10,000) | 가능 | 함대 규모 계획. 실제 값은 Service Quotas 콘솔에서 확인 |
| 저장 설정 채널 수 | 100 | 가능 | 저장 모드를 넓게 쓰려면 사전 증설 |
| viewer 연결(채널당) | 10 | 가능 | 늘려도 디바이스 업링크가 진짜 한계다([16장](/study/webrtc/16-aws-landscape)) |
| master 연결(채널당) | 1 | 불가 | 디바이스 한 대당 채널 하나. 같은 채널에 두 번 붙으면 최근 연결이 이긴다 |
| 연결 최대 시간 | 3,600초 | 불가 | 1시간 전에 선제 재연결 |
| idle timeout | 600초 | 불가 | viewer가 없는 master는 끊긴다고 전제하고 재연결 |
| GO_AWAY 유예 | 60초 | 불가 | 받은 메시지 처리 후 즉시 재연결 |
| ConnectAsMaster / ConnectAsViewer | 채널당 3 TPS | 불가 | 재연결 루프에 백오프 필수 |
| DescribeSignalingChannel / GetSignalingChannelEndpoint | 계정 300 TPS, 채널당 5 TPS | 불가 | 엔드포인트 캐시 |
| GetIceServerConfig | 채널당 5 TPS(불가), 계정·리전 100 TPS(가능) | 혼합 | 대량 재연결 시 계정 한도에 걸린다 |
| SendSdpOffer / SendSdpAnswer | WebSocket 연결당 5 TPS | 불가 | viewer가 한꺼번에 들어오면 master의 answer가 밀린다 |
| SendIceCandidate | WebSocket 연결당 20 TPS | 불가 | viewer 여럿의 후보가 master 연결 하나로 나간다 |
| 메시지 payload | 10 KB | 불가 | SDP를 부풀리는 확장·코덱 나열을 피한다 |
| TURN 대역폭 / allocation / credential | 세션당 5 Mbps / 채널당 50 / 300초 | 불가 | relay 비트레이트 상한, credential 재발급 |
| JoinStorageSession | 세션 1시간, idle 3분, 비트레이트 1 Mbps(가능) | 혼합 | 21장 참고 |
| JoinStorageSessionAsViewer | 세션당 3명, 세션 1시간, idle 1분 | 불가 | 21장 참고 |

조정 불가 한도에서 나오는 설계 포인트 세 가지를 짚는다.

<strong>대량 재연결의 동시성.</strong> 리전 쪽 순단이나 통신사 장애가 끝나면 디바이스 수백 대가 같은 순간에 재연결을 시도한다. 채널당 3 TPS는 디바이스 하나에게는 넉넉하지만, `GetSignalingChannelEndpoint`(계정 300 TPS)와 `GetIceServerConfig`(계정 100 TPS) 같은 계정 단위 한도는 함대 전체가 나눠 쓴다. 재연결에는 반드시 지수 백오프와 <strong>무작위 지터</strong>를 넣고, 엔드포인트는 캐시해서 재연결 때마다 다시 묻지 않게 한다.

<strong>master 연결 하나에 몰리는 메시지.</strong> `SendIceCandidate` 20 TPS와 `SendSdpAnswer` 5 TPS는 WebSocket 연결 단위다. viewer는 각자 연결이 있지만 master는 연결 하나로 모든 viewer에게 answer와 후보를 보낸다. 운영자 10명이 한꺼번에 같은 트랙터를 열면 master는 answer 10건과 후보 수십~백 건을 1~2초 안에 보내야 하고, 한도에 걸린다. viewer 입장 시점을 백엔드에서 조금씩 엇갈리게 하거나, 불필요한 후보(예: 쓰지 않는 인터페이스의 host 후보)를 줄인다.

<strong>할당량 확인과 신청.</strong> 채널 수처럼 문서마다 숫자가 다른 항목은 문서를 인용하지 말고 콘솔 값을 기준으로 한다. Service Quotas의 서비스 코드는 이름으로 먼저 찾는다.

```bash
aws service-quotas list-services --region ap-northeast-2 \
  --query "Services[?contains(ServiceName, 'Kinesis Video')]"
# 찾은 ServiceCode로 현재 값 조회
aws service-quotas list-service-quotas --service-code <위에서 찾은 코드> --region ap-northeast-2 \
  --query "Quotas[].{name:QuotaName,value:Value,adjustable:Adjustable}" --output table
```

## 7. 흔한 장애와 대응

장시간 켜져 있는 디바이스는 여러 개의 "만료 시계"를 동시에 돌린다. 장애 대부분은 이 중 하나를 놓쳐서 생긴다.

![장시간 디바이스가 관리해야 하는 만료 시계 타임라인(0~75분). 시그널링 WSS는 최대 1시간·idle 10분 한도가 있어 45분 서술과 60분 한도선보다 앞선 약 40분(±지터)에 선제 재연결해 연결 #2로 넘어간다. GO_AWAY 대응 레인에서는 32분쯤 GO_AWAY를 받으면 60초 안에 메시지를 처리하고 재연결한다. TURN 자격증명은 Ttl 300초 고정이라 5분 간격 칸으로 표시되고, 새 PeerConnection이나 ICE restart 때마다 GetIceServerConfig를 다시 호출한다. IoT 임시 자격증명은 role alias 기본 3,600초이며 만료 전인 약 50분에 갱신해 #2로 넘어간다](/images/study-webrtc/22-connection-timeline-light.png)
![장시간 디바이스가 관리해야 하는 만료 시계 타임라인(0~75분). 시그널링 WSS는 최대 1시간·idle 10분 한도가 있어 45분 서술과 60분 한도선보다 앞선 약 40분(±지터)에 선제 재연결해 연결 #2로 넘어간다. GO_AWAY 대응 레인에서는 32분쯤 GO_AWAY를 받으면 60초 안에 메시지를 처리하고 재연결한다. TURN 자격증명은 Ttl 300초 고정이라 5분 간격 칸으로 표시되고, 새 PeerConnection이나 ICE restart 때마다 GetIceServerConfig를 다시 호출한다. IoT 임시 자격증명은 role alias 기본 3,600초이며 만료 전인 약 50분에 갱신해 #2로 넘어간다](/images/study-webrtc/22-connection-timeline-dark.png)

### 장애 표

| 증상 | 원인 | 확인 | 대응 |
|---|---|---|---|
| 부팅 직후 모든 KVS 호출이 서명 오류·403 | <strong>시계 오차로 SigV4 실패</strong>. RTC 배터리가 없는 보드는 전원이 끊기면 1970년이나 빌드 시각으로 돌아간다. 서명 시각이 AWS 시각과 허용 범위 이상 벌어지면 요청이 거절된다. 시계가 크게 틀리면 TLS 인증서 유효기간 검증부터 실패하기도 한다 | 디바이스 `date`와 NTP 상태, 오류 메시지의 시각 문구 | KVS SDK를 시작하기 전에 NTP/chrony 동기화를 기다린다. 농기계라면 GPS 시각을 보조 시간원으로 쓴다. 브라우저는 JS SDK `SignalingClient`의 `systemClockOffset`으로 보정한다 |
| 한동안 잘 되다가 재연결부터 실패 | <strong>임시 자격증명 만료</strong>. IoT role alias 자격증명은 기본 3,600초, 운영자 STS 자격증명은 발급 시 정한 시간이 지나면 만료된다 | 자격증명 `expiration`과 실패 시각 비교 | 디바이스는 만료 전에 credentials provider에서 다시 받는다. 환경변수에 고정한 임시 키(`AWS_SESSION_TOKEN` 포함)는 만료되면 프로세스를 다시 띄우기 전까지 복구되지 않는다. 브라우저는 재연결 직전에 백엔드에서 새 자격증명을 받는다 |
| 정확히 약 1시간마다 새 viewer가 못 붙음 | <strong>1시간 연결 한도에서 재연결 누락</strong>. 시그널링 연결은 최대 3,600초(조정 불가)다. 끊긴 뒤 다시 붙지 않은 master는 새 viewer의 offer를 받지 못한다 | `Failure`(`ConnectAsMaster`) 시각, 디바이스 로그의 close 시각 | 1시간이 되기 전에 선제 재연결한다. `GO_AWAY`를 받으면 60초 안에 재연결하고, `RECONNECT_ICE_SERVER`를 받으면 ICE 서버 설정을 새로 받는다. 시그널링이 끊길 때 이미 맺어진 PeerConnection의 미디어가 바로 끊기는지는 문서에서 확인하지 못했으므로 두 경우 모두에 대비한다 |
| viewer가 없을 때 디바이스가 조용히 오프라인 | <strong>10분 idle timeout</strong>. 메시지가 오가지 않으면 600초 후 서비스가 연결을 닫고 그 클라이언트를 offline으로 표시한다 | close 이벤트 간격이 약 10분 | close 이벤트마다 백오프 재연결하는 루프를 기본으로 둔다. "연결 유지"가 아니라 "끊기면 다시 붙기"로 설계한다 |
| 일부 운영자만 접속 실패 | <strong>viewer 한도 초과</strong>. 채널당 10명(조정 가능)을 넘으면 `ClientLimitExceededException`, 저장 세션은 3명이다. 같은 `ClientId`로 다시 연결하면 새 연결이 기존 연결을 대체하므로, 탭 두 개가 같은 ID를 쓰면 서로를 밀어낸다 | `Failure`(`ConnectAsViewer`), 오류 타입 | 백엔드가 좌석을 관리하고 대기·거절 메시지를 준다. `ClientId`는 "운영자 + 탭" 단위로 안정적으로 만든다. 상시 10명 이상이 필요하면 증설보다 구조 변경(16장)을 먼저 검토한다 |
| 연결은 됐는데 검은 화면, 또는 answer 거절 | <strong>코덱 불일치</strong>. 디바이스가 보내는 H.264 프로파일·패킷화 모드를 상대가 받지 않거나, 저장 모드에 VP8·H.265를 보냈다 | SDP의 `a=rtpmap`·`a=fmtp`(profile-level-id), `statusResponse` | 양쪽 코덱 우선순위를 맞춘다(`setCodecPreferences`, [04장](/study/webrtc/04-sdp-jsep)). 저장 모드는 H.264 + Opus만. 메시지에 `correlationId`를 넣어 거절 사유를 받는다 |
| `iceConnectionState`가 `failed`, 특정 사무실·회선에서만 | <strong>NAT/방화벽의 UDP 차단</strong>. 직결도, UDP TURN도 막혔다 | `getStats()`의 후보 목록에 relay가 있는지, 어떤 전송인지 | System requirements 문서는 TURN 엔드포인트로 `turn:`과 `turns:`(TLS) 443을 함께 적는다. 브라우저가 TCP/TLS 443 relay로 붙을 수 있게 둔다. 디바이스 방화벽은 `*.kinesisvideo.{region}.amazonaws.com`의 443(TCP와 UDP)을 허용한다. IPv6만 열린 망은 System requirements 문서상 STUN/TURN 미지원임에 주의한다 |
| 디바이스 두 대가 번갈아 끊김 | <strong>master 중복 접속</strong>. 같은 채널에 master가 두 번 붙으면 가장 최근 요청이 이긴다 | 같은 채널의 `ConnectAsMaster` 빈도 | thing 이름·채널 이름 중복(교체 장비에 옛 인증서 재사용 등)을 레지스트리에서 막는다 |
| ICE restart나 재접속 후 relay만 실패 | <strong>TURN credential 만료</strong>. `GetIceServerConfig`의 자격증명은 300초 고정이다 | ICE 서버 설정을 받은 시각과 PeerConnection 생성 시각 | 새 PeerConnection을 만들거나 ICE restart를 할 때마다 `GetIceServerConfig`를 다시 호출한다. 오래 캐시한 설정을 재사용하지 않는다 |

`GetIceServerConfig`의 `SessionExpiredException` 설명에는 "연결 후 세션은 45분간 유효하다"는 문장도 있다. 1시간 최대 연결 시간과 숫자가 달라 의미가 분명하지 않다. 선제 재연결 시점을 1시간보다 넉넉히 앞당겨 잡는 편이 이런 모호함에서도 안전하다.

### 진단 순서

장애 신고를 받으면 다음 순서로 범위를 좁힌다. 세부 도구 사용법은 [15장](/study/webrtc/15-monitoring-debugging)에 있다.

1. <strong>시그널링 단계인가, 미디어 단계인가.</strong> CloudWatch `Failure`를 `Operation`별로 본다. ConnectAs 계열이 실패하면 자격증명·시계·한도 문제이고, 시그널링은 성공했는데 영상이 안 나오면 ICE·코덱 문제다.
2. <strong>시그널링이면</strong>: 디바이스 시계, 자격증명 만료 시각, IAM 정책의 리소스 이름(ThingName 헤더 포함), viewer 한도 순서로 확인한다.
3. <strong>미디어면</strong>: 브라우저 `chrome://webrtc-internals`와 `getStats()`로 후보 쌍 상태를 보고, 디바이스는 `AWS_KVS_LOG_LEVEL`을 올려 ICE 로그를 받는다. `KVS_ICE_TRANSPORT_POLICY=relay`로 TURN 경로만 따로 시험하면 "직결 실패"인지 "TURN까지 실패"인지 갈린다.
4. <strong>간헐적이면</strong>: 1시간·10분·5분 같은 주기성이 있는지 본다. 주기가 보이면 거의 항상 위 표의 만료 시계 중 하나다.

::: tip 핵심 정리
- IAM은 디바이스(MASTER)·운영자(VIEWER)·프로비저닝 백엔드로 역할을 나눈다. 디바이스는 `${credentials-iot:ThingName}`으로 자기 채널에만, 운영자는 STS 세션 정책으로 채널 하나에만, 백엔드는 `managed-by` 태그 조건으로 자기 리소스에만 손대게 한다. 채널 ARN 끝에는 생성 시각이 붙으므로 이름 뒤를 와일드카드로 둔다.
- 연결 없는 채널은 과금되지 않지만 할당량·보안·저장 비용 때문에 디바이스 폐기 시 지운다. 순서는 인증서 폐기 → 저장 모드 해제 → 채널 삭제 → 스트림 처리다.
- CloudWatch는 시그널링 실패·지연·메시지, TURN 분, 저장 분을 보여 주지만 P2P 미디어 품질은 보여 주지 못한다. 품질은 브라우저 `getStats()`와 C SDK `rtcPeerConnectionGetMetrics()`로 양 끝에서 모은다. 네임스페이스는 `list-metrics`로 확인하고 추측하지 않는다.
- 비용은 활성 채널 + 메시지 + TURN 분(+ 데이터 전송)이고, 대개 TURN이 지배한다. 서울 기준 200대 예시는 relay 20%에서 월 약 $32, 60%에서 약 $75이며 relay 데이터 전송료가 별도로 붙는다.
- master 1, 연결 1시간, idle 10분, TURN 5 Mbps·300초는 조정할 수 없다. 재연결 루프·지터 백오프·credential 재발급을 설계에 넣고, 문서마다 다른 채널 수 한도는 Service Quotas 콘솔 값을 기준으로 한다.
:::

## 다음 챕터

[Amazon Chime SDK](/study/webrtc/23-chime-sdk)에서는 P2P인 KVS와 달리 SFU로 동작하는 회의 모델, Meeting/Attendee API와 백엔드 역할, Media Pipelines를 살펴보고 디바이스 영상 플랫폼에 맞는 지점과 맞지 않는 지점을 따져 본다.
